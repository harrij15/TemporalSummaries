
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
    
    
    attr_index = -2
    age = 22
    activity_level = "active"   
    #tw = 7
    attributes = ["Stock Market Data","Step Counts","Heart Rate","ActivFit","Calorie Intake"]
    attr = attributes[attr_index]
    
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
        
    if tw == 365:
        TW = "years"
    elif tw == 30:
        TW = "months"
    elif tw == 7:
        TW = "weeks"
    elif tw == 1:
        TW = "days"    
    
    df_list = get_data_list([df_index],attr) 
    
    # TODO: Modify this to handle multiple time series
    data = df_list[0]
    db_fn_prefix = "series_db_" + str(df_index)
    alpha_size = 5
    alphabet = string.ascii_lowercase
    path = "C:\Users\harrij15\Documents\GitHub\RPI-HEALS\\"
    cygwin_path = r"C:\Apps\cygwin64\bin"
    #n = 10000 
    n = 1
    
    letter_map = dict()  
    for i in range(alpha_size):
        letter_map[alphabet[i]] = i+1
        
    proto_cnt = 0
        
    full_sax_rep = ''
    if attr == "ActivFit":
        attr = "Activity"
        activities = data[["ActivFit"]]
        dates = data[["date"]]
        
        activities = activities.values.tolist()
        dates = dates.values.tolist()
        
        data_dict = dict()
        for i in range(len(activities)):
            letter = None
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
        
        full_sax_rep = ts_to_string(znorm(np.array(data)), cuts_for_asize(alpha_size))
        print full_sax_rep
        print len(full_sax_rep)
                
        # Summaries for the past full week
        week_sax = ts_to_string(paa(znorm(np.array(data)),int(len(data)/tw)), cuts_for_asize(alpha_size))
        print week_sax
        #print cuts_for_asize(alpha_size)
        #print paa(znorm(np.array(data)),int(len(data)/tw))

        past_week_letter = week_sax[-1]
        prev_week_letter = week_sax[-2]
        other_week_letter = week_sax[len(week_sax)/2]
        prev_start_day = tw*(len(week_sax)-2)
        start_day = tw*(len(week_sax)-1)
        end_day = tw*len(week_sax)
        #print start_day,end_day
        past_week = data[start_day:end_day]
        #raw_input(full_sax_rep[start_day:end_day])
        
        #Overall week summary (week granularity)
        summarizer_type = "Weekly " + attr
        week_summary, week_summarizer = get_single_SAX_summary(summarizer_type,attr,past_week_letter,letter_map,alpha_size)
        #t2 = time.time()
        print "Overall week summary (week granularity):", week_summary
        #print "Time taken: ", float(t2 - t1)/n
        print    
        proto_cnt += 1
        
        # Overall week summary (week granularity) - for Heart Rate comparison
        if attr == "Heart Rate":
            summarizer_type = "Weekly " + attr
        
            hr = sum(past_week)/tw
            
            
            summary = HR_Summary(hr,age,activity_level)
            print "Overall week summary (week granularity) - Heart Rate:", summary
            print    
            proto_cnt += 1    
    
    
    # Overall week summary (day granularity)
    summarizers = ["very low","low","moderate","high","very high"]
    summary = None
    summarizer_type = "Past Daily Week - " + attr 
    if attr == "Activity":
        day_list = sorted(data_dict.keys())
        prev_day = day_list[-1]
        day_sax = data_dict[prev_day]
        summary_data = day_sax
        x_vals = "activities tracked"
        summarizers = ["walking","inactive","in a vehicle"]
    else:
        summary_data = full_sax_rep[start_day:end_day]
        x_vals = "days"
        
    t1_list, quantifier_list, summary_list = generate_summaries(summarizers,summarizer_type,attr,summary_data,letter_map,alpha_size,TW=TW,xval=x_vals) 
    if quantifier_list != None:
        summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
        truth = max(t1_list)
    
    if summary != None:
        print "Overall week summary (day granularity):", summary
        print "Truth value:", truth
        #print summary_list, t1_list
        print        
        proto_cnt += 1
        
    # Overall week summary (day granularity) - Heart Rate
    if attr == "Heart Rate":
        hr_summarizers = ["abnormally low","low","within range","high","abnormally high"]
        summary = None

        summarizer_type = "Past Daily Week - " + attr        
        t1_list, quantifier_list, summary_list = generate_summaries(hr_summarizers,summarizer_type,attr,data[start_day:end_day],letter_map,alpha_size,TW=TW,xval=x_vals) 
        if quantifier_list != None:
            summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
            truth = max(t1_list)
            
        if summary != None:
            print "Overall week summary (day granularity) - Heart Rate:", summary
            #print "Truth value:", truth
            print        
            proto_cnt += 1    
    
    if attr != "Heart Rate" and attr != "Activity":
        # Standard comparison summary
        summarizer_type = "Weekly " + attr
        comparison_summary = comparison_SAX_summary(summarizer_type,attr,prev_week_letter,past_week_letter)
        if comparison_summary != None:
            print "Standard comparison summary (day granularity):", comparison_summary
            print    
            proto_cnt += 1
            
        comparison_summary = comparison_SAX_summary(summarizer_type,attr,other_week_letter,past_week_letter,other_week_index=len(week_sax)/2,tw=7)
        if comparison_summary != None:
            print "Standard comparison summary (day granularity):", comparison_summary
            print    
            proto_cnt += 1        
    elif attr == "Heart Rate":
        # Standard comparison summary - Heart Rate            
        comparison_summary = comparison_HR_summary(data[prev_start_day:start_day],data[start_day:end_day],age,activity_level)
        if comparison_summary != None:
            print "Standard comparison summary (day granularity) - Heart Rate:", comparison_summary
            print    
            proto_cnt += 1        
    elif attr == "Activity":
        # Standard comparison summary - Activity
        other_day = data_dict[day_list[0]]
        prev_day = data_dict[day_list[-2]]
        curr_day = data_dict[day_list[-1]]
        
        comparison_summary = comparison_activ(prev_day,curr_day)
        if comparison_summary != None:
            print "Standard comparison summary (day granularity) - Activity:", comparison_summary
            print    
            proto_cnt += 1      
            
        comparison_summary = comparison_activ(other_day,curr_day,other_index=0)
        if comparison_summary != None:
            print "Standard comparison summary (day granularity) - Activity:", comparison_summary
            print    
            proto_cnt += 1          
    
        
    # Simple goal summary
    stepcounts_daylist = [395,94,2953,10048,552,1098,31,3173,2673,2443,733,1388,238,828,0,1128,14,1363,0,282]    
    guideline_summarizers = ["reached","did not reach"]

    t1_list, quantifier_list, summary_list = generate_summaries(guideline_summarizers,attr,attr,data,letter_map,alpha_size)
    if quantifier_list != None:
        goal_summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
        truth = max(t1_list)
    else:
        goal_summary = ""
    
    if len(goal_summary) != 0:
        print "Simple goal summary:", goal_summary
        print "Truth value:", truth
        print
        proto_cnt += 1
    
    
    # Standard trend summary
    if attr == "Activity":
        trend_list = []
        lim = len(data_dict.keys())-1
        for i in range(len(sorted(data_dict.keys()))-1):
            key = data_dict.keys()[i]
            next_key = data_dict.keys()[i+1]
            
            trend_list.append(data_dict[key].count("w") - data_dict[next_key].count("w"))            
    else:
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
        week_comparisons = find_similar_weeks(data,week_sax)
        #print week_comparisons
        pattern_summarizers = ["rose","dropped","stayed the same"]
        summarizer_type = "Pattern Recognition - " + attr
        t1_list, quantifier_list, summary_list = generate_summaries(pattern_summarizers,summarizer_type,attr,week_comparisons,letter_map,alpha_size)
        if summary_list != None:
            pattern_summary = summary_list[best_quantifier_index(quantifier_list,t1_list)]
            truth = max(t1_list)
            print "Pattern recognition summary:", pattern_summary 
            print "Truth value:", truth
            print
            
        if summary_list != None:
            proto_cnt += 1
             
    # Output pattern summaries from cSPADE
    if attr == "Heart Rate":
        hr_sax = ""
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
        print "SPADE Patterns - Heart Rate:"
        num_proto = analyze_patterns(attr,hr_sax,hr_alphabet,hr_letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,proto_cnt,flag_="HR")
        print
        
    elif attr == "Activity":
        activ_letter_map = {
            "w" : 1,
            "s" : 2,
            "v" : 3
        }
        
        activ_alphabet = "wsv"
        print "SPADE Patterns - Activity:"
        num_proto = analyze_patterns(attr,day_sax,activ_alphabet,activ_letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,proto_cnt,flag_="HR")
        print      
    else:
        print "SPADE Patterns:"
        num_proto = analyze_patterns(attr,full_sax_rep,alphabet,letter_map,tw,alpha_size,db_fn_prefix,path,cygwin_path,proto_cnt)
    
    print
    print "Number of summaries produced:", num_proto
    #print '\a'