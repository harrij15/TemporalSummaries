
####### MAIN PROGRAM #######

if __name__ == "__main__":
    from proto_lib import *
    import json
    import matplotlib.pyplot as plt
    from datetime import datetime
    import numpy as np
    from alpha_vantage.timeseries import TimeSeries
    
    from saxpy.alphabet import cuts_for_asize
    from saxpy.znorm import znorm
    from saxpy.sax import ts_to_string
    
    from saxpy.paa import paa
    from saxpy.hotsax import find_discords_hotsax
    from squeezer import *
    import random   
    import string
    import time
    
    attributes = ["Stock Market Data","Step Counts","Heart Rate","ActivFit","Calorie Intake"]    
    
    # Input parameters
    attr_index = 1 # Chooses the attribute in attributes list
    age = 22
    activity_level = "active"   
    alpha_size = 5    
    
    # Parameters for SPADE
    min_conf = 0.5    
    min_sup = 0.15
    path = "" # Path for pattern data
    cygwin_path = r"" # Path to Cygwin
    
    attr = attributes[attr_index]
        
    # Based on the attribute, choose data and time window
    if attr == "Stock Market Data":
        df_index = 1
        tw = 7
    elif attr == "ActivFit":
        df_index = 539
        tw = 1
    elif attr == "Calorie Intake":
        df_index = 0
        tw = 7
    else:
        df_index = 106
        tw = 7
        
    # Choose string for time window based on tw
    if tw == 365:
        TW = "years"
    elif tw == 30:
        TW = "months"
    elif tw == 7:
        TW = "weeks"
    elif tw == 1:
        TW = "days"    
    
    # Retrieve data
    df_list = get_data_list([df_index],attr) 
    
    data = df_list[0]
    db_fn_prefix = "series_db_" + str(df_index)
    alphabet = string.ascii_lowercase
    singular_TW = TW[:-1]

    # Construct mapping from letters in alphabet to integers (starting at 1)
    letter_map = dict()  
    for i in range(alpha_size):
        letter_map[alphabet[i]] = i+1
        
    # Counter for number of summaries produced
    proto_cnt = 0
        
    full_sax_rep = ''
    if attr == "ActivFit": # Categorical activity data
        
        # Gather data
        attr = "Activity"
        activities = data[["ActivFit"]]
        dates = data[["date"]]
        
        activities = activities.values.tolist()
        dates = dates.values.tolist()
        
        # Construct mapping from date to sequence of letters
        data_dict = dict()
        for i in range(len(activities)):
            letter = None
            
            # Construct alphabet for data
            if activities[i][0] == "walking":
                letter = "w"
            elif activities[i][0] == "still":
                letter = "s"
            elif activities[i][0] == "in_vehicle":
                letter = "v"
                
            date_list = dates[i][0].split(" ")
            date = date_list[0]
            date = datetime.strptime(date,"%Y-%m-%d")
            if date not in data_dict.keys():
                data_dict[date] = letter
            else:
                data_dict[date] += letter
                
    else:
        # SAX representation at daily granularity (sub-time window assumed to be days)
        full_sax_rep = ts_to_string(znorm(np.array(data)), cuts_for_asize(alpha_size))
                
        # SAX representation at time window granularity
        tw_sax = ts_to_string(paa(znorm(np.array(data)),int(len(data)/tw)), cuts_for_asize(alpha_size))

        # Focus on past tw along with previous tw's
        past_tw_letter = tw_sax[-1]
        prev_tw_letter = tw_sax[-2]
        other_tw_letter = tw_sax[len(tw_sax)/2]
        
        # Get indices for days at beginning and end of tw's
        prev_start_day = tw*(len(tw_sax)-2)
        start_day = tw*(len(tw_sax)-1)
        end_day = tw*len(tw_sax)
        
        past_tw = data[start_day:end_day]
        
        # Overall TW summary (TW granularity) - for Heart Rate comparison
        if attr == "Heart Rate":
            first = singular_TW.capitalize() + "ly "
            summarizer_type = first + attr
        
            # Calculate average heart rate
            hr = sum(past_tw)/tw
            
            summary = HR_Summary(hr,age,activity_level,singular_TW)
            print "Overall" + singular_TW + " summary (" + first.lower() + "granularity):", summary
            print    
            proto_cnt += 1  
        else:
            # Overall TW summary (TW granularity)
            first = singular_TW.capitalize() + "ly "
            summarizer_type = first + attr
            tw_summary, tw_summarizer = get_single_SAX_summary(summarizer_type,attr,past_tw_letter,letter_map,alpha_size,singular_TW)
            print "Overall " + singular_TW + " summary (" + first.lower() + "granularity):", tw_summary
            print    
            proto_cnt += 1  
    
    # Overall TW summary (sTW granularity)
    summarizers = ["very low","low","moderate","high","very high"]
    summary = None
    summarizer_type = "Past Daily TW - " + attr 
    
    if attr == "Activity": # Get SAX for previous day granularity
        day_list = sorted(data_dict.keys())
        prev_day = day_list[-1]
        day_sax = data_dict[prev_day]
        summary_data = day_sax
        x_vals = "activities tracked"
        summarizers = ["walking","inactive","in a vehicle"]
    else:
        summary_data = full_sax_rep[start_day:end_day]
        x_vals = "days"
        
    # Overall week summary (day granularity) - Heart Rate
    if attr == "Heart Rate":
        hr_summarizers = ["abnormally low","low","within range","high","abnormally high"]
        summary = None

        summarizer_type = "Past Daily TW - " + attr        
        t1_list, quantifier_list, summary_list = generate_summaries(hr_summarizers,summarizer_type,attr,data[start_day:end_day],letter_map,alpha_size,TW=TW,xval=x_vals) 
        if quantifier_list != None:
            summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
            truth = max(t1_list)
            
        if summary != None:
            print "Overall week summary (daily granularity):", summary
            print     
            proto_cnt += 1  
    else:
        t1_list, quantifier_list, summary_list = generate_summaries(summarizers,summarizer_type,attr,summary_data,letter_map,alpha_size,TW=TW,xval=x_vals) 
        
        if quantifier_list != None:
            summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
            truth = max(t1_list)
        
        if summary != None:
            print "Overall week summary (daily granularity):", summary
            print "Truth value:", truth
            print     
            proto_cnt += 1  
    
    # Comparison summary
    if attr != "Heart Rate" and attr != "Activity":

        # Standard comparison summary for previous week and week before it
        summarizer_type = "Weekly " + attr
        comparison_summary = comparison_SAX_summary(summarizer_type,attr,prev_tw_letter,past_tw_letter)
        if comparison_summary != None:
            print "Standard comparison summary (daily granularity):", comparison_summary
            print  
            proto_cnt += 1  
            
        # Standard comparison summary for previous week and another week
        comparison_summary = comparison_SAX_summary(summarizer_type,attr,other_tw_letter,past_tw_letter,other_week_index=len(tw_sax)/2,tw=7)
        if comparison_summary != None:
            print "Standard comparison summary (daily granularity):", comparison_summary
            print  
            proto_cnt += 1  

    elif attr == "Heart Rate":
        # Standard comparison summary - Heart Rate            
        comparison_summary = comparison_HR_summary(data[prev_start_day:start_day],data[start_day:end_day],age,activity_level,singular_TW)
        if comparison_summary != None:
            print "Standard comparison summary (daily granularity) - Heart Rate:", comparison_summary
            print    
            proto_cnt += 1  

    elif attr == "Activity":
        
        # Standard comparison summary - Activity
        other_day = data_dict[day_list[0]]
        prev_day = data_dict[day_list[-2]]
        curr_day = data_dict[day_list[-1]]
        
        comparison_summary = comparison_activ(prev_day,curr_day)
        if comparison_summary != None:
            print "Standard comparison summary (daily granularity) - Activity:", comparison_summary
            print    
            proto_cnt += 1      
            
        comparison_summary = comparison_activ(other_day,curr_day,other_index=0)
        if comparison_summary != None:
            print "Standard comparison summary (daily granularity) - Activity:", comparison_summary
            print    
            proto_cnt += 1          
    
        
    # Goal evaluation summary
    guideline_summarizers = ["reached","did not reach"]
    t1_list, quantifier_list, summary_list = generate_summaries(guideline_summarizers,attr,attr,data,letter_map,alpha_size)
    if quantifier_list != None:
        goal_summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
        truth = max(t1_list)
    else:
        goal_summary = ""
    
    if len(goal_summary) != 0:
        print "Goal evaluation summary:", goal_summary
        print "Truth value:", truth
        print    
        proto_cnt += 1  
    
    # Standard trend summary
    if attr == "Activity":
        
        # Different approach for categorical data
        trend_list = []
        lim = len(data_dict.keys())-1
        
        # Walking -> active; else -> not active
        for i in range(len(sorted(data_dict.keys()))-1):
            key = data_dict.keys()[i]
            next_key = data_dict.keys()[i+1]
            
            # Compare active counts
            trend_list.append(data_dict[key].count("w") - data_dict[next_key].count("w"))            
    else:
        # Get differences between days
        trend_list = pd.DataFrame(data).diff().values.T.tolist() 
        trend_list = trend_list[0]    
        
    trend_summarizers = ["increases","decreases","does not change"]
    summarizer_type = "Trends"
    t1_list, quantifier_list, summary_list = generate_summaries(trend_summarizers,summarizer_type,attr,trend_list,letter_map,alpha_size)
    if quantifier_list != None:
        trend_summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
        truth = max(t1_list)
    print "Standard trend summary:", trend_summary   
    print "Truth value:", truth
    print
    proto_cnt += 1  
        
    # Pattern recognition summary
    if attr != "Activity":
        
        tw_comparisons, indices = find_similar_tw(data,tw_sax)
        
        # If comparisons are found, clusters visualized as different colors on raw data
        if len(tw_comparisons) > 0:
            display_clusters(data,indices)
            
        pattern_summarizers = ["rose","dropped","stayed the same"]
        summarizer_type = "Pattern Recognition - " + attr
        t1_list, quantifier_list, summary_list = generate_summaries(pattern_summarizers,summarizer_type,attr,tw_comparisons,letter_map,alpha_size)
        if summary_list != None:
            pattern_summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
            truth = max(t1_list)
            print "Pattern recognition summary:", pattern_summary 
            print "Truth value:", truth
            print
            
        if summary_list != None:
            proto_cnt += 1
             
    # Output pattern summaries from SPADE algorithm
    if attr == "Heart Rate":
        hr_sax = ""
        
        # Create s representation for heart rate
        for i in range(len(data)):
            summarizer = hr_evaluation(data[i], age, activity_level)
            if summarizer == "abnormally low":
                hr_sax += "a"
            elif summarizer == "low":
                hr_sax += "l"
            elif summarizer == "within range":
                hr_sax += "w"
            elif summarizer == "high":
                hr_sax += "h"
            else:
                hr_sax += "b"
        
        hr_letter_map = {"a" : 1,
                      "l" : 2,
                      "w" : 3,
                      "h" : 4,
                      "b" : 5}
        
        hr_alphabet = "alwhb"
        summary_list, num_proto = analyze_patterns(attr,hr_sax,hr_alphabet,hr_letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,flag_="HR")        
    elif attr == "Activity":
        activ_letter_map = {
            "w" : 1,
            "s" : 2,
            "v" : 3
        }
        
        activ_alphabet = "wsv"
        summary_list, num_proto = analyze_patterns(attr,day_sax,activ_alphabet,activ_letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,flag_="HR")
    else:
        summary_list, num_proto = analyze_patterns(attr,full_sax_rep,alphabet,letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt)
        
    for i in range(len(summary_list)):
        print summary_list[i]
    
    print
    print "Number of summaries produced:", num_proto
