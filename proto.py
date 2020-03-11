#! python3
####### MAIN PROGRAM #######

if __name__ == "__main__":
    from proto_lib import *
    import json
    import matplotlib.pyplot as plt
    import datetime
    import numpy as np
    from alpha_vantage.timeseries import TimeSeries
    
    from saxpy.paa import paa
    from saxpy.hotsax import find_discords_hotsax
    
    import string
    import time
    import csv
    
    attributes = ["Stock Market Data","Weather","WeatherHourly"]    
    
    # Input parameters
    attr_index = 0 # Chooses the attribute in attributes list
    age = 23
    activity_level = "active"   
    alpha_size = 5
    alpha = 0.9 # For alpha cut 
    all_cnt = 0
    user_cnt = 0
    ada_goal = None
    arm_dict = dict()
    
    # Parameters for SPADE
    min_conf = 0.8
    min_sup = 0.2
    treatment = None
    path = "" # Path for pattern data
    cygwin_path = r"" # Path to Cygwin
        
    date_columns = { "Weather" : "DATE", 
                     "WeatherHourly" : "DATE",
                     "Stock Market Data" : "date"
                     }
    
    weekday_dict = { 1 : "Monday",
                     2 : "Tuesday",
                     3 : "Wednesday",
                     4 : "Thursday",
                     5 : "Friday",
                     6 : "Saturday",
                     7 : "Sunday" }     
    
    reverse_summ_map = {"very low" : 0,
                        "low" : 1,
                        "moderate" : 2,
                        "high" : 3,
                        "very high" : 4,
                        "reached" : 5,
                        "did not reach" : 6,
                        "increases" : 7,
                        "decreases" : 8,
                        "does not change" : 9
                        }
    
    summarizer_7 = ["extremely low","very low","low","moderate","high","very high","extremely high"]
    
    attr = attributes[attr_index]           
        
    # Based on the attribute, choose data and time window
    if attr == "Stock Market Data":
        df_index_list = [1]
        tw = 7
    elif attr == "Weather":
        df_index_list = [3]
        tw = 7      
    elif attr == "WeatherHourly":
        df_index_list = [2]
        tw = 0.04       
        
    # Choose string for time window based on tw
    if tw == 365:
        TW = "years"
    elif tw == 30:
        TW = "months"
    elif tw == 7:
        TW = "weeks"
    elif tw == 1:
        TW = "days"   
    elif tw == 0.04:
        TW = "hours"
    else:
        TW = None
        
    df_index_str = ""
    for index in df_index_list:
        df_index_str += "_" + str(index)
        break
    db_fn_prefix = "series_db" + str(df_index_str)
    alphabet = string.ascii_lowercase
    
    if TW != None:
        singular_TW = TW[:-1]
    else:
        singular_TW = ''

    # Construct mapping from letters in alphabet to integers (starting at 1)
    letter_map = dict()  
    for i in range(alpha_size):
        letter_map[alphabet[i]] = i+1    
        
    # Counter for number of summaries produced
    proto_cnt = 0  
    
    # Retrieve data
    df_lists, pid_list = get_data_list(df_index_list,attr) 
    
    summary_dict = dict()
    df_index = -1
    for df_list in df_lists:
        df_index += 1
        
        sax_list = []
        tw_sax_list = []
        data_list = []
        summary_data_list = []
        past_full_wks = []        

        # Retrieve date column
        tmp = attr
        
        if type(df_list) is list:
            df_list = df_list[0]
        date_column_list = [df_list[key] for key in df_list.keys() if key == date_columns[tmp]]
        date_column = date_column_list[0].copy()
        
        for i in range(len(date_column)):
            date = date_column[i]
            
            # Parse dates
            if attr == "Weather":
                date = date.split('/')
                date = datetime.datetime(int(date[2]),int(date[0]),int(date[1]))  
            elif attr == "WeatherHourly":
                date = date.split('T')
                day_str = date[0]
                hour_str = date[1]
                
                day_str = day_str.split('-')
                hour_str = hour_str.split(':')
                
                date = datetime.datetime(10,int(day_str[0]),int(day_str[1]),int(hour_str[0]),int(hour_str[1]),int(hour_str[2]))
            elif attr == "Stock Market Data":
                date = date.split('/')
                date = datetime.datetime(int(date[2]),int(date[0]),int(date[1]))

            week_day = date.weekday()
            week_day = weekday_dict[week_day+1]        
            date_column[i] = week_day
        
        ### Between series
        from itertools import combinations
        key_dict = {"Stock Market Data" : ["AAPL close value","AET close value"],
                    "Weather" : ["Average Temperature","Average Wind Speed"],
                    "WeatherHourly" : ["Average Temperature","Average Wind Speed"],
                    "close value" : ["close value"],
                    "temperature": ["temperature"]
                    }
        
        df_key_dict = {"AAPL close value" : "AAPL close value",
                       "AET close value" : "AET close value",
                       "Average Temperature" : "Average Temperature",
                       "Average Wind Speed" : "Average Wind Speed",
                       "Alabama temperature" : "Alabama temperature",
                       "Alaska temperature" : "Alaska temperature",                           
                       "temperature" : "temperature"
                       }
        
        attr_list = key_dict[attr]             
        summary = None
    
        # Try different combinations of attributes
        combos = []
        for i in range(len(attr_list)):
            comb = combinations(attr_list,i+1)
            combos.append(list(comb))

        track = []
        for combo in combos:
            
            for key_list in combo:
                key_list = list(key_list)
                if key_list in track:
                    continue
                else:
                    track.append(key_list)
                
                for i in range(len(key_list)):
                    if key_list[i] == "Stock Market Data":
                        key_list[i] = "close value"                   
                
                alphabet_list = []
                letter_map_list = []
                alpha_sizes = []
                sax_list = []
                tw_sax_list = []
                goals = None
                
                if attr == "StepUp":
                    goals = df_list["Baseline"]                  
                elif attr == "Cue" or attr == "Arm Comparison":
                    continue
                
                summary_data_list = []
                            
                # Fill info lists corresponding to keys
                error = False
                for i in range(len(key_list)):
                    if attr == "Calorie Intake":
                        data = df_list[attr]
                    else:
                        data = df_list[df_key_dict[key_list[i]]]
                                                  
                    if len(data) < tw:
                        error = True
                        break
                    
                    data_list.append(data)
                    alphabet_list.append(alphabet)
                    letter_map_list.append(letter_map)       
                    alpha_sizes.append(alpha_size)                    
                    
                    if key_list[i] != "Activity" and attr != "MyFitnessPalMeals":
                        full_sax_rep = ts_to_string(znorm(np.array(data)), cuts_for_asize(alpha_sizes[i]))
                       
                        if tw > 0.04:
                            tw_sax = ts_to_string(paa(znorm(np.array(data)),int(len(data)/tw)), cuts_for_asize(alpha_sizes[i]))
                            tw_sax_list.append(tw_sax)      
                            
                            prev_start_day = int(tw*(len(tw_sax)-2))
                            start_day = int(tw*(len(tw_sax)-1))
                            end_day = int(tw*len(tw_sax))
                            other_start_day = int(tw*(len(tw_sax)/2))
                            other_end_day = int(tw*(len(tw_sax)/2)+tw)
                            
                            past_full_wks.append(data[start_day:end_day]) 
                            
                            other_tw = data[other_start_day:other_end_day]
                            other_day_sax = full_sax_rep[other_start_day:other_end_day]
                            other_days = date_column[other_start_day:other_end_day]  
                        else:
                            start_day = 0
                            end_day = len(full_sax_rep)
                                                                                
                        
                        
                        summary_data = full_sax_rep[start_day:end_day]
                    else: 
                        summary_data = full_sax_rep[start_day:end_day]
                        x_vals = "days"          
                                                                             
                    sax_list.append(full_sax_rep)  
                    summary_data_list.append(summary_data)
                
                if error:
                    continue
                                    
                
                # Multivariate standard evaluation summaries (TW granularity)
                if "close value" in key_list: 
                    for i in range(len(key_list)):
                        key_list[i] = pid_list[i] + " " + key_list[i]
                if "Activity" not in key_list and tw > 0.04 and attr != "MyFitnessPalMeals":
                    sub_dict = dict()
                    past_tw_letters = []        
                    first = singular_TW.capitalize() + "ly "
                    summarizer_type = "Weekly "
                    if attr == "Heart Rate":
                        index = key_list.index("Heart Rate")
                        hr = sum(past_full_wks[index])/tw
                        tw_summary, tw_summarizers = HR_Summary(hr,age,activity_level,singular_TW)
                    else:
                        for i in range(len(key_list)):
                            past_tw_letters.append(tw_sax_list[i][-1])
                            summarizer_type += key_list[i]
                            
                            if i != len(key_list)-1:
                                summarizer_type += " and "        
                        
                        tw_summary, tw_summarizers = get_single_SAX_summary(key_list,past_tw_letters,letter_map_list,alpha_sizes,singular_TW,tw_size=tw,past_tw=past_full_wks,age=age,activity_level=activity_level)
                    
                    if tw_summary != None:
                        if tw_summary not in sub_dict.keys():
                            sub_dict[tw_summary] = dict()
                            
                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[tw_summary].keys():
                                sub_dict[tw_summary][treatment] = 1
                            else:
                                sub_dict[tw_summary][treatment] += 1                            
                            
                        print("Overall " + singular_TW + " summary (" + first.lower() + "granularity):", tw_summary)
                        length = get_summary_length(len(tw_summarizers))
                        simplicity = get_simplicity(len(tw_summarizers)+1)
                        
                        query_ = [["current index",[len(tw_sax)-1]]]   
                        t3, coverage = degree_of_covering(key_list,tw_sax_list,tw_summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
                        t4 = degree_of_appropriateness(key_list,tw_sax_list,tw_summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)   
                        print("Covering:", t3)
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print()
                        proto_cnt += 1   
                        
                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                for j in range(len(key_list)):
                                    key_list_str += key_list[j]
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                                
                                for j in range(len(tw_summarizers)):
                                    summ_str += tw_summarizers[j]
                                    if j != len(tw_summarizers)-1:
                                        summ_str += ", "                                   
                                datawriter.writerow([pid,key_list_str,tw,'SETW','',summ_str])    
                        
                    if "SETW" not in summary_dict.keys():
                        summary_dict["SETW"] = sub_dict
                    else:

                        for key in sub_dict:
                            if key in summary_dict["SETW"].keys() and treatment in summary_dict["SETW"][key].keys():
                                summary_dict["SETW"][key][treatment] += 1
                            else:
                                if key not in summary_dict["SETW"].keys():
                                    summary_dict["SETW"][key] = dict()
                                summary_dict["SETW"][key][treatment] = 1                    
                            
                # Multivariate standard evaluation summaries (sTW granularity)
                # Overall TW summary (sTW granularity)
                summarizer_type = "Past Daily TW - "
                sub_dict = dict()
                
                for i in range(len(key_list)):
                    summarizer_type += key_list[i]
                    
                    if i != len(key_list)-1:
                        summarizer_type += " and "
            
                
                    
                summarizer_list = []
                for i in range(len(key_list)):
                    summarizers = ["very low","low","moderate","high","very high"]
                    if alpha_size == 7:
                        summarizers = summarizer_7                    
                    summarizer_list.append(summarizers)
                
                past_tw_list = [sax[start_day:end_day] for sax in sax_list]
            
                possible_summarizers = summarizer_list
                avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizer_list,summarizer_type,key_list,past_tw_list,letter_map_list,alpha_sizes,alpha,xval="days",TW=TW,age=age,activity_level=activity_level)
                if quantifier_list != None:

                    index = best_quantifier_index(quantifier_list,t1_list)
                    daily_summary = summary_list[index]
                    summarizer_list = summarizer_list[index]
                    truth = t1_list[index]
                    average = avg_list[index]
                                        
                    if daily_summary != None:
                        if daily_summary not in sub_dict.keys():
                            sub_dict[daily_summary] = dict()

                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[daily_summary].keys():
                                sub_dict[daily_summary][treatment] = 1
                            else:
                                sub_dict[daily_summary][treatment] += 1                              
                        print("Day summary (daily granularity):", daily_summary)
                        print("Truth value:", truth)
                        length = get_summary_length(len(summarizer_list))
                        simplicity = get_simplicity(len(summarizer_list)+1)
                        query_ = [["through",start_day,end_day]]
                        
                        t2 = degree_of_imprecision(avg_list)
                        t3, coverage = degree_of_covering(key_list,sax_list,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
                        t4 = degree_of_appropriateness(key_list,sax_list,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)    
                        print("Imprecision:", t2)
                        print("Covering:", t3)
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print()
                        proto_cnt += 1
                        
                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                q_str = ""
                                for j in range(len(key_list)):
                                    key_list_str += key_list[j]
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                                
                                for j in range(len(summarizer_list)):
                                    summ_str += summarizer_list[j]
                                    if j != len(summarizer_list)-1:
                                        summ_str += ", "      
                                        
                                datawriter.writerow([pid,key_list_str,tw,'SEsTW',quantifier_list[index],summ_str])      
                           
                if "SESTW" not in summary_dict.keys():
                    summary_dict["SESTW"] = sub_dict
                else:

                    for key in sub_dict:
                        if key in summary_dict["SESTW"].keys() and treatment in summary_dict["SESTW"][key].keys():
                            summary_dict["SESTW"][key][treatment] += 1
                        else:
                            if key not in summary_dict["SESTW"].keys():
                                summary_dict["SESTW"][key] = dict()
                            summary_dict["SESTW"][key][treatment] = 1
                            
                # Multivariate standard evaluation summary with specified qualifier (sTW)
                sub_dict = dict()
                summarizer_type = "Past Daily TW w/ Qualifier- "
                for i in range(len(key_list)):
                    summarizer_type += key_list[i]
                
                    if i != len(key_list)-1:
                        summarizer_type += " and " 
                        
                summarizers = ["very low","low","moderate","high","very high"]
                if alpha_size == 7:
                    summarizers = summarizer_7
                summarizer_list = []
                for i in range(len(key_list)):
                    summarizer_list.append(summarizers)   
                    
                if attr == "MyFitnessPalMeals":
                    summarizer_list = [summarizer_list[0]]
                    
                if key_list[i] == "Activity":
                    past_tw_list = [day_sax]
                else:
                    past_tw_list = [sax[start_day:end_day] for sax in sax_list]
                    
                key_combos = []
                for i in range(len(key_list)):
                    key_comb = combinations(key_list,i+1)
                    key_combos.append(list(key_comb))  
                
                # TODO: get rid of repeats
                for key_combo in key_combos:
                    for flag_ in key_combo:
                        flag_ = list(flag_)
                        if len(flag_) == len(key_list) or attr == "MyFitnessPalMeals":
                            continue
                                                    
                        avg_list, t1_list, quantifier_list, summary_list, summarizers_list = generate_summaries(summarizer_list,summarizer_type,key_list,past_tw_list,letter_map_list,alpha_sizes,alpha,TW=TW,xval="days",flag=flag_)
                        if quantifier_list != None:
                            index = best_quantifier_index(quantifier_list,t1_list)
                            summary = summary_list[index]
                            summarizers_list = summarizers_list[index]
                            truth = t1_list[index]
                            average = avg_list[index]
                    
                        if summary != None:
                            if summary not in sub_dict.keys():
                                sub_dict[summary] = dict()

                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[summary].keys():
                                    sub_dict[summary][treatment] = 1
                                else:
                                    sub_dict[summary][treatment] += 1                                 
                            print("Overall " + singular_TW + " summary w/ ",end="")
                            for i in range(len(flag_)):
                                print(flag_[i],end="")
                                if i != len(flag_)-1:
                                    print(" and ",end="")
                            print(" qualifier (daily granularity): " +  summary)
                            print("Truth value:", truth)
                         
                            length = get_summary_length(len(summarizers_list))
                            simplicity = get_simplicity(len(summarizers_list)+len(flag_)+1)
                            query_ = [["qualifier",flag_,summarizers,alphabet_list],["through",start_day,end_day]]
                            t2 = degree_of_imprecision(avg_list)
                            t3, coverage = degree_of_covering(key_list,sax_list,summarizers_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
                            t4 = degree_of_appropriateness(key_list,sax_list,summarizers_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level) 
                            print("Imprecision:",t2)
                            print("Covering:",t3)
                            print("Appropriateness:", t4)
                            print("Relevance:", coverage)
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print()
                            proto_cnt += 1   
                            
                            if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                with open(arm_filepath,"a",newline='') as csvfile:
                                    pid = pid_list[df_index]
                                    datawriter = csv.writer(csvfile)
                                    key_list_str = ""
                                    summ_str = ""
                                    flag_str = ""
                                    q_str = ""
                                    index_list = []
                                    for j in range(len(key_list)):
                                        if key_list[j] in flag_:
                                            continue
                                        
                                        key_list_str += key_list[j]
                                        index_list.append(j)
                                        if j != len(key_list)-1:
                                            key_list_str += ", "
                                      
                                            
                                    for j in range(len(flag_)):
                                        flag_str += flag_[j]
                                        j_ = key_list.index(flag_[j])
                                        index_list.append(j_)
                                        if j != len(flag_)-1:
                                            flag_str += ", "      
                                            
                                    for j in range(len(index_list)):
                                        index_ = index_list[j]
                                        summ_str += summarizers_list[index_]
                                        if j != len(index_list)-1:
                                            summ_str += ", "    
                                            
                                    datawriter.writerow([pid,key_list_str.strip(', ')+"|"+flag_str.strip(', '),tw,'SEsTWQ',quantifier_list[index],summ_str,flag_str])                                 
                             
                if "SESTWQ" not in summary_dict.keys():
                    summary_dict["SESTWQ"] = sub_dict
                else:
                    for key in sub_dict:
                        if key in summary_dict["SESTWQ"].keys() and treatment in summary_dict["SESTWQ"][key].keys():
                            summary_dict["SESTWQ"][key][treatment] += 1
                        else:
                            if key not in summary_dict["SESTWQ"].keys():
                                summary_dict["SESTWQ"][key] = dict()
                            summary_dict["SESTWQ"][key][treatment] = 1      
                            
                # Multivariate evaluation comparison summaries
                sub_dict = dict()
                if ("Activity" not in key_list and tw_sax_list != None and len(tw_sax_list) != 0) or tw == 0.04:
                    error = False
                    summarizer_type = "Weekly " 
                    prev_tw_letters = []
                    past_tw_letters = []
                    if tw == 0.04:
                        tw_sax_list = sax_list
                    first_index = len(tw_sax_list[0])-2
                    second_index = len(tw_sax_list[0])-1
                    for i in range(len(key_list)):
                        if len(tw_sax_list[i]) < 2:
                            error = True
                            continue
                        past_tw_letters.append(tw_sax_list[i][second_index])
                        prev_tw_letters.append(tw_sax_list[i][first_index])
                            
                        summarizer_type += key_list[i]
                    
                        if i != len(key_list)-1:
                            summarizer_type += " and "    
                    
                    if not error:
                        comparison_summary, summarizer_list, goal_list = comparison_TW_SAX_summary(summarizer_type,key_list,prev_tw_letters,past_tw_letters,TW,letter_map_list,first_index,second_index,flag="eval")
                        if comparison_summary != None:
                            if comparison_summary not in sub_dict.keys():
                                sub_dict[comparison_summary] = dict()

                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[comparison_summary].keys():
                                    sub_dict[comparison_summary][treatment] = 1
                                else:
                                    sub_dict[comparison_summary][treatment] += 1                                
                                
                            print("Standard evaluation comparison summary (" + singular_TW + "ly granularity): " + comparison_summary)
                            length = get_summary_length(len(summarizer_list))
                            simplicity = get_simplicity(len(summarizer_list)+1) 
                            
                            if second_index == -1:
                                past_ = len(tw_sax)-1
                            else:
                                past_ = second_index
                                
                            if first_index == -1:
                                prev_ = len(tw_sax)-1
                            else:
                                prev_ = first_index   
                            
                            query_ = [["current index",[past_,prev_]]]
                            flag_ = "compare"
                            if attr == "Heart Rate":
                                flag_ = "compareHR"
                                
                            t3, coverage = degree_of_covering(key_list,tw_sax_list,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag_)
                            t4 = degree_of_appropriateness(key_list,tw_sax_list,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)  
                            t2 = degree_of_imprecision(avg_list)
                            print("Covering:",t3)                                
                            print("Appropriateness:", t4)
                            print("Relevance:", coverage)
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print() 
                            proto_cnt += 1   
                            
                            if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                with open(arm_filepath,"a",newline='') as csvfile:
                                    pid = pid_list[df_index]
                                    datawriter = csv.writer(csvfile)
                                    key_list_str = ""
                                    summ_str = ""
                                    flag_str = ""
                                    q_str = ""
                                    index_list = []
                                    for j in range(len(key_list)):
                                        key_list_str += key_list[j]
                                        if j != len(key_list)-1:
                                            key_list_str += ", "
                                      
                                            
                                    for j in range(len(summarizer_list)):
                                        summ_str += summarizer_list[j]
                                        if j != len(summarizer_list)-1:
                                            summ_str += ", "         
                                            
                                    datawriter.writerow([pid,key_list_str,tw,'EC',None,summ_str,None])                                
                                        
                    if "EC" not in summary_dict.keys():
                        summary_dict["EC"] = sub_dict
                    else:
                        for key in sub_dict:
                            if key in summary_dict["EC"].keys() and treatment in summary_dict["EC"][key].keys():
                                summary_dict["EC"][key][treatment] += 1
                            else:
                                if key not in summary_dict["EC"].keys():
                                    summary_dict["EC"][key] = dict()
                                summary_dict["EC"][key][treatment] = 1            
                     
                # Multivariate goal comparison summaries
                weather_flag = False
                for attr_ in attr_list:
                    if "temperature" in attr_ or attr_ == "Average Temperature" or "close value" in attr_:
                        weather_flag = True
                        break
                
                if not weather_flag and attr != "MyFitnessPalMeals":
                    sub_dict = dict()
                    summarizer_type = "Weekly Goal " 
                    prev_tw_letters = []
                    past_tw_letters = []    
                    past_index = int(len(tw_sax_list[0])/2)-1
                    prev_index = -2                    
                    error = False
                    for i in range(len(key_list)):
                        if key_list[i] == "Heart Rate":
                            prev_tw_letters.append(sum(data_list[i][prev_start_day:start_day])/7)
                            past_tw_letters.append(sum(data_list[i][start_day:end_day])/7)
                            if len(tw_sax_list[i]) < 2:
                                error = True
                                continue
                        elif key_list[i] == "Activity":
                            other_day = data_dict[day_list[0]]
                            prev_day = data_dict[day_list[-2]]
                            curr_day = data_dict[day_list[-1]]                        
                            prev_tw_letters.append(prev_day)
                            past_tw_letters.append(curr_day)
                        else:        

                            if len(tw_sax_list) == 0 or len(tw_sax_list[i]) < 2:
                                error = True
                                continue  
                            past_tw_letters.append(tw_sax_list[i][past_index])            
                            prev_tw_letters.append(tw_sax_list[i][prev_index])
                        
                        if key_list[i] == "step count":
                            key_list[i] = "Step Count" 
                            
                        summarizer_type += key_list[i]
                        
                        if i != len(key_list)-1:
                            summarizer_type += " and "    
                            
                    if not error:

                        if key_list[i] == "Heart Rate":
                            prev_tw_letters = [prev_tw_letters]
                            past_tw_letters = [past_tw_letters]
                        comparison_summary, summarizer_list, goal_list = comparison_TW_SAX_summary(summarizer_type,key_list,prev_tw_letters,past_tw_letters,TW,letter_map_list,first_index,second_index,age=age,activity_level=activity_level)

                        if comparison_summary != None:
                            if comparison_summary not in sub_dict.keys():
                                sub_dict[comparison_summary] = dict()

                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[comparison_summary].keys():
                                    sub_dict[comparison_summary][treatment] = 1
                                else:
                                    sub_dict[comparison_summary][treatment] += 1                              
                            if singular_TW == "day":
                                print("Goal comparison summary (daily granularity): " + comparison_summary)
                            else:
                                print("Goal comparison summary (" + singular_TW + "ly granularity): " + comparison_summary)
                                
                            length = get_summary_length(len(summarizer_list))
                            simplicity = get_simplicity(len(summarizer_list)+1) 
                            
                            if past_index == -1:
                                past_ = len(tw_sax)-1
                            else:
                                past_ = past_index
                                
                            if prev_index == -1:
                                prev_ = len(tw_sax)-1
                            else:
                                prev_ = prev_index   
                            
                            query_ = [["current index",[past_,prev_]]]    
                            
                            flag_ = "compare"
                            if attr == "Heart Rate":
                                flag_ = "compareHRGoal"                            
                            t3, coverage = degree_of_covering(key_list,tw_sax_list,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag_)
                            t4 = degree_of_appropriateness(key_list,tw_sax_list,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)  
                            print("Covering:",t3)                                
                            print("Appropriateness:", t4)
                            print("Relevance:", coverage)
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print()   
                            proto_cnt += 1   
                            
                            if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                with open(arm_filepath,"a",newline='') as csvfile:
                                    pid = pid_list[df_index]
                                    datawriter = csv.writer(csvfile)
                                    key_list_str = ""
                                    summ_str = ""
                                    goal_str = ""
                                    index_list = []
                                    for j in range(len(key_list)):
                                        key_list_str += key_list[j]
                                        if j != len(key_list)-1:
                                            key_list_str += ", "
                            
                                    for j in range(len(summarizer_list)):
                                        summ_str += summarizer_list[j]
                                        if j != len(summarizer_list)-1:
                                            summ_str += ", "  
                                            
                                    for j in range(len(goal_list)):
                                        goal_str += goal_list[j]
                                        if j != len(goal_list)-1:
                                            goal_str += ", "                                          
                                    datawriter.writerow([pid,key_list_str,tw,'GC',None,summ_str,goal_str])                            
                                        
                        if "GC" not in summary_dict.keys():
                            summary_dict["GC"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["GC"].keys() and treatment in summary_dict["GC"][key].keys():
                                    summary_dict["GC"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["GC"].keys():
                                        summary_dict["GC"][key] = dict()
                                    summary_dict["GC"][key][treatment] = 1 

                # Goal evaluation summaries
                weather_flag = False
                for attr_ in attr_list:
                    if "temperature" in attr_ or attr_ == "Average Temperature" or "close value" in attr_:
                        weather_flag = True
                        break
                
                if attr != "Stock Market Data" and "close value" not in attr and ("temperature" not in attr or attr != "Average Temperature") and not weather_flag and attr != "MyFitnessPalMeals":
                    sub_dict = dict()
                    guideline_summarizers = ["reached","did not reach"]
                    if attr == "StepUp" or ada_goal != None:
                        guideline_summarizers = ["reached"]
                    summarizers_list = []
                    for i in range(len(key_list)):
                        summarizers_list.append(guideline_summarizers)
                    if attr == "Activity":
                        past_tw = []
                        for letter in summary_data:
                            past_tw.append(categ_eval(letter))
                            
                    summarizer_type = "Goal Evaluation - "
                    for i in range(len(key_list)):
                        if key_list[i] == "step count":
                            key_list[i] = "Step Count"  
                            
                        summarizer_type += key_list[i]
                        if i != len(key_list)-1:
                            summarizer_type += " and "
                            
                    past_tw_list = []
                    for i in range(len(key_list)):
                        if key_list[i] == "Activity":
                            continue
                        else:
                            past_tw_list.append(data_list[i][start_day:end_day])
                        
                    input_goals = [goals]
                    if attr == "MyFitnessPal":
                        input_goals = goals
                        
                    avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizers_list,summarizer_type,key_list,past_tw_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,TW=TW,goals=input_goals,ada_goal=ada_goal)
                    
                    if quantifier_list != None:
                        index = best_quantifier_index(quantifier_list,t1_list)
                        goal_summary = summary_list[index]
                        summarizers = summarizer_list[index]
                        truth = t1_list[index]
                        average = avg_list[index]
                    else:
                        goal_summary = ""   
                                    
                    if len(goal_summary) != 0:
    
                        if goal_summary not in sub_dict.keys():
                            sub_dict[goal_summary] = dict()

                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[goal_summary].keys():
                                sub_dict[goal_summary][treatment] = 1
                            else:
                                sub_dict[goal_summary][treatment] += 1                        
                        print("Goal evaluation summary:", goal_summary)
                        print("Truth value:", truth)

                        query_ = [["through",start_day,end_day]]
                        if attr == "StepUp" or attr == "MyFitnessPal" or attr == "MyFitnessPalMeals":
                            
                            t3, coverage = degree_of_covering(key_list,data_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,goals=input_goals,quantifier=quantifier_list[index])
                        else:
                            flag_ = None
                            if attr == "Heart Rate":
                                flag_ = "HR"                            
                            t3, coverage = degree_of_covering(key_list,data_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,goals=input_goals[0],flag=flag_)
                        
                        t4 = degree_of_appropriateness(key_list,data_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,goals=input_goals)
                        
                        length = get_summary_length(len(summarizers))
                        simplicity = get_simplicity(len(summarizers)+1)
                        t2 = degree_of_imprecision(avg_list)
                        print("Imprecision:",t2)
                        print("Covering:",t3)                            
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1
                        
                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                goal_str = ""
                                index_list = []
                                for j in range(len(key_list)):
                                    key_list_str += key_list[j]
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                        
                                for j in range(len(summarizers)):
                                    summ_str += summarizers[j]
                                    if j != len(summarizers)-1:
                                        summ_str += ", "  
                                        
                                for j in range(len(key_list)):
                                    if key_list[j] == "StepUp" or key_list[j] == "Step Count":
                                        goal_str += "above their baseline"
                                    else:
                                        goal_str += "low"
                                    if j != len(key_list)-1:
                                        goal_str += ", "                                          
                                        
                                datawriter.writerow([pid,key_list_str,tw,'GE',quantifier_list[index],summ_str,goal_str])                              
                            
                        if "GE" not in summary_dict.keys():
                            summary_dict["GE"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["GE"].keys() and treatment in summary_dict["GE"][key].keys():
                                    summary_dict["GE"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["GE"].keys():
                                        summary_dict["GE"][key] = dict()
                                    summary_dict["GE"][key][treatment] = 1    
                                
                # Standard trends summaries
                if attr != "MyFitnessPalMeals":
                    sub_dict = dict()
                    trend_lists = []
                    for i in range(len(key_list)):
                        data = data_list[i]
                        if key_list[i] == "Activity":
                                        
                            # Different approach for categorical data
                            trend_list = []
                            lim = len(data_dict.keys())-1
                            
                            # Walking -> active; else -> not active
                            for i in range(len(sorted(data_dict.keys()))-1):
                                curr_key = data_dict.keys()[i]
                                next_key = data_dict.keys()[i+1]
                                
                                # Compare active counts
                                trend_list.append(data_dict[curr_key].count("w") - data_dict[next_key].count("w"))   
                        else:
                            trend_list = pd.DataFrame(data).diff().values.T.tolist() 
                            trend_list = trend_list[0]    
                            
                        
                        trend_lists.append(trend_list)
                    
                    trend_summarizers = ["increases","decreases","does not change"]
                    summarizers_list = []
                    for i in range(len(key_list)):
                        summarizers_list.append(trend_summarizers) 
                        
                    summarizer_type = "Trends " 
                    for i in range(len(key_list)):
                        if key_list[i] == "step count":
                            key_list[i] = "Step Count"   
                            
                        summarizer_type += key_list[i]
                        if i != len(key_list)-1:
                            summarizer_type += " and "        
   
                    avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizers_list,summarizer_type,key_list,trend_lists,letter_map_list,alpha_sizes,alpha,TW=TW)
                    if quantifier_list != None:
                        index = best_quantifier_index(quantifier_list,t1_list)
                        trend_summary = summary_list[index]
                        summarizers = summarizer_list[index]
                        truth = t1_list[index]
                        average = avg_list[index]
                        print("Standard trend summary:", trend_summary)
                        print("Truth value:", truth)
                        
                        if trend_summary not in sub_dict.keys():
                            sub_dict[trend_summary] = dict()
                            
                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[trend_summary].keys():
                                sub_dict[trend_summary][treatment] = 1
                            else:
                                sub_dict[trend_summary][treatment] += 1                           
                        t3, coverage = degree_of_covering(key_list,trend_lists,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,flag=None)
                        t4 = degree_of_appropriateness(key_list,trend_lists,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)               
                        length = get_summary_length(len(summarizers))
                        simplicity = get_simplicity(len(summarizers))
                        t2 = degree_of_imprecision(avg_list)
                        print("Imprecision:",t2)
                        print("Covering:",t3)                        
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1 
                        
                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                goal_str = ""
                                index_list = []
                                for j in range(len(key_list)):
                                    key_list_str += key_list[j]
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                        
                                for j in range(len(summarizers)):
                                    summ_str += summarizers[j]
                                    if j != len(summarizers)-1:
                                        summ_str += ", "  
                                           
                                        
                                datawriter.writerow([pid,key_list_str,tw,'ST',quantifier_list[index],summ_str,None])                                                
                    
                        if "ST" not in summary_dict.keys():
                            summary_dict["ST"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["ST"].keys() and treatment in summary_dict["ST"][key].keys():
                                    summary_dict["ST"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["ST"].keys():
                                        summary_dict["ST"][key] = dict()
                                    summary_dict["ST"][key][treatment] = 1       
                                
                # Multivariate cluster-based pattern summaries
                sub_dict = dict()
                if "Activity" not in key_list and TW != None and TW != "hours":
                    combined_sax = []
                    sep_sax_list = []
                    for i in range(len(sax_list)):
                        sep_sax_list.append([list(sax_list[i][j:j+tw]) for j in range(0,len(sax_list[i]),tw)])
                        
                    chunked_sax = sep_sax_list[0]
                    for i in range(1,len(sep_sax_list)):
                        
                        for j in range(len(sep_sax_list[i])):
                            for k in range(len(sep_sax_list[i][j])):
                                chunked_sax[j][k] += "-" + sep_sax_list[i][j][k]
                             
                    cluster_data = None
                    indices = None
                    try:
                        tw_index = -1
                        [cluster_data, indices] = series_clustering(full_sax_rep,tw_sax_list,tw,flag=chunked_sax,week_index=tw_index)
                    except TypeError:
                        cluster_data = None
                        indices = None
                    
                    pattern_summarizers = ["rose","dropped","stayed the same"]
                    summarizers_list = []
                    for i in range(len(key_list)):
                        summarizers_list.append(pattern_summarizers)  
                        
                    if cluster_data != None and len(cluster_data) != None:
                        summarizer_type = "Pattern Recognition - " 
                        for i in range(len(key_list)):
                            if key_list[i] == "step count":
                                key_list[i] = "Step Count"      
                                
                            summarizer_type += key_list[i]
                            if i != len(key_list)-1:
                                summarizer_type += " and "  
                        
                        avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizers_list,summarizer_type,key_list,cluster_data,letter_map_list,alpha_sizes,alpha,tw_index=tw_index)

                        extension = "In " + TW[:-1] + " " + str(tw_index) + ","
                        last_summarizer = ""
                        num_summarizers = 0
                        temp_flag = False
                        if type(attr_list) is list:
                            for j in range(len(attr_list)):
                                if "temperature" in attr_list[j] or attr_list[j] == "Average Temperature":
                                    temp_flag = True
                        else:
                            if "temperature" in attr_list or attr_list == "Average Temperature":
                                temp_flag = True                            
                        for i in range(len(key_list)):
                            summary_data = summary_data_list[i]
                            
                            attribute_ = key_list[i]
                            if not temp_flag:
                                attribute_ = attribute_.lower()                                
                            extension += " your " + attribute_ + " was"
                            for letter in summary_data:
                                summarizer = evaluateSAX(letter,letter_map_list[i],alpha_sizes[i])
                                if last_summarizer != summarizer:
                                    if last_summarizer != "":
                                        extension += ", then "
                                    else:
                                        extension += " " 
                                    extension += summarizer
                                    last_summarizer = summarizer
                                    num_summarizers += 1
                                    
                            if i != len(summary_data_list)-1:
                                extension += " and"
                            last_summarizer = ""
                                
                        extension += "."
                        
                        if quantifier_list != None:
                            index = best_quantifier_index(quantifier_list,t1_list)
                            cluster_summary = summary_list[index]
                            summarizers = summarizer_list[index]
                            truth = t1_list[index]
     
                            cluster_summary = extension + " " + cluster_summary
                            
                            if cluster_summary not in sub_dict.keys():
                                sub_dict[cluster_summary] = dict()
  
                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[cluster_summary].keys():
                                    sub_dict[cluster_summary][treatment] = 1
                                else:
                                    sub_dict[cluster_summary][treatment] += 1                                     
                            print("Cluster-based pattern summary:", cluster_summary)
                            print("Truth value:", truth)
                            query_ = [["current index", indices]]
                            
                            
                            t3, coverage = degree_of_covering(key_list,tw_sax_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag="compare")
                            t4 = degree_of_appropriateness(key_list,tw_sax_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag="compare")
                                
                            # To count the summarizer in pattern_summarizers
                            num_summarizers += len(key_list)
                            length = get_summary_length(num_summarizers)
                            simplicity = get_simplicity(num_summarizers+1)
                            t2 = degree_of_imprecision(avg_list)
                            print("Imprecision:",t2)
                            print("Covering:",t3)                                
                            print("Appropriateness:", t4)
                            print("Relevance:", coverage)
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print() 
                            proto_cnt += 1 
                            if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                with open(arm_filepath,"a",newline='') as csvfile:
                                    pid = pid_list[df_index]
                                    datawriter = csv.writer(csvfile)
                                    key_list_str = ""
                                    summ_str = ""
                                    goal_str = ""
                                    index_list = []
                                    for j in range(len(key_list)):
                                        key_list_str += key_list[j]
                                        if j != len(key_list)-1:
                                            key_list_str += ", "
                            
                                    for j in range(len(summarizers)):
                                        summ_str += summarizers[j]
                                        if j != len(summarizers)-1:
                                            summ_str += ", "  
                                               
                                            
                                    datawriter.writerow([pid,key_list_str,tw,'CB',None,summ_str,None])                                  
                                   
                            if "CB" not in summary_dict.keys():
                                summary_dict["CB"] = sub_dict
                            else:
                                for key in sub_dict:
                                    if key in summary_dict["CB"].keys() and treatment in summary_dict["CB"][key].keys():
                                        summary_dict["CB"][key][treatment] += 1
                                    else:
                                        if key not in summary_dict["CB"].keys():
                                            summary_dict["CB"][key] = dict()
                                        summary_dict["CB"][key][treatment] = 1  
                                
                    # Multivariate standard pattern summaries
                    sub_dict = dict()
                    if cluster_data != None:
                        num_summarizers = 0
                        first_letters = []
                        second_letters = []
                        for i in range(len(cluster_data)):
                            first_letters.append(cluster_data[i][-1][0])
                            second_letters.append(cluster_data[i][-1][1])
                            
                        num_summarizers = len(first_letters)
                        sp_summary, summarizer_list = standard_pattern_summary(first_letters,second_letters,key_list,tw_index)
                        if sp_summary not in sub_dict.keys():
                            sub_dict[sp_summary] = dict()

                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[sp_summary].keys():
                                sub_dict[sp_summary][treatment] = 1
                            else:
                                sub_dict[sp_summary][treatment] += 1                            
                        print("Standard pattern summary:", sp_summary)
                        query_ = [["current index", [indices[-1]]]]
                        t3, coverage = degree_of_covering(key_list,tw_sax_list,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag="compare")
                        t4 = degree_of_appropriateness(key_list,tw_sax_list,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag="compare")                    
                        length = get_summary_length(num_summarizers)
                        simplicity = get_simplicity(num_summarizers+1)
                        print("Covering:",t3)                            
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1    

                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                goal_str = ""
                                index_list = []
                                for j in range(len(key_list)):
                                    key_list_str += key_list[j]
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                        
                                for j in range(len(summarizer_list)):
                                    summ_str += summarizer_list[j]
                                    if j != len(summarizer_list)-1:
                                        summ_str += ", "  
                                           
                                        
                                datawriter.writerow([pid,key_list_str,tw,'SP',None,summ_str,None])                             
                                  
                        if "SP" not in summary_dict.keys():
                            summary_dict["SP"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["SP"].keys() and treatment in summary_dict["SP"][key].keys():
                                    summary_dict["SP"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["SP"].keys():
                                        summary_dict["SP"][key] = dict()
                                    summary_dict["SP"][key][treatment] = 1           
                                
                    # Multivariate if-then pattern summaries
                    sub_dict = dict()
                    if tw > 0:
                        summarizer_type = "If-then pattern "
                        for i in range(len(key_list)):
                            if key_list[i] == "step count":
                                key_list[i] = "Step Count"   
                                
                            summarizer_type += key_list[i]
                            if i != len(key_list)-1:
                                summarizer_type += " and " 
                        
                        if attr == "Heart Rate":
                            sax_list = [hr_sax]
                            
                        summary_list, supports, proto_cnt, numsum_list, summarizers_list = analyze_patterns(key_list,sax_list,alphabet_list,letter_map_list,weekday_dict,tw,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt)
                        weekday_summaries, supports_, proto_cnt, numsum_list_, summarizers_list_ = analyze_patterns(key_list,sax_list,alphabet_list,letter_map_list,weekday_dict,tw,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,weekdays=date_column)  
                        if len(summary_list):
                            print("If-then pattern summaries")
                            
                        for i in range(len(summary_list)):
                            print(summary_list[i])
                            if summary_list[i] not in sub_dict.keys():
                                sub_dict[summary_list[i]] = dict() 
                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[summary_list[i]].keys():
                                    sub_dict[summary_list[i]][treatment] = 1
                                else:
                                    sub_dict[summary_list[i]][treatment] += 1                                
                            summ_index = 0
                            summ_list = []
                            while summ_index < len(key_list) and (attr == "MyFitnessPalMeals" and summ_index == 0):
                                sublist = []
                                
                                for j in range(len(summarizers_list[i])):
                                    sublist += summarizers_list[i][j][summ_index]
                                summ_list.append(sublist)
                                summ_index += 1
                            
                            if attr == "Heart Rate":
                                sax_list = [data]                                
                            t4 = degree_of_appropriateness(key_list,sax_list,summ_list,summarizer_type,supports[i],letter_map_list,alpha_sizes,age,activity_level)   
                            print("Covering:",t3)                                
                            print("Appropriateness:", t4)
                            print("Relevance:", supports[i])
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print()  
    
                        if "IT" not in summary_dict.keys():
                            summary_dict["IT"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["IT"].keys() and treatment in summary_dict["IT"][key].keys():
                                    summary_dict["IT"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["IT"].keys():
                                        summary_dict["IT"][key] = dict()
                                    summary_dict["IT"][key][treatment] = 1                               
                        print()
                        
                        sub_dict = dict()
                        for i in range(len(weekday_summaries)):
                            print(weekday_summaries[i])
                            if weekday_summaries[i] not in sub_dict.keys():
                                sub_dict[weekday_summaries[i]] = dict()

                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[weekday_summaries[i]].keys():
                                    sub_dict[weekday_summaries[i]][treatment] = 1
                                else:
                                    sub_dict[weekday_summaries[i]][treatment] += 1                                   
                            summ_index = 0
                            summ_list_ = []      
                            while summ_index < len(key_list) and (attr == "MyFitnessPalMeals" and summ_index == 0): 
                                sublist = []  
                                for j in range(len(summarizers_list_[i])):
                                    sublist += summarizers_list_[i][j][summ_index]
                                summ_list_.append(sublist)
                                summ_index += 1
        
                            t4 = degree_of_appropriateness(key_list,sax_list,summ_list_,summarizer_type,supports_[i],letter_map_list,alpha_sizes,age,activity_level,flag=date_column)   
                            print("Covering:",t3)                                
                            print("Appropriateness:", t4)
                            print("Relevance:", supports_[i])                   
                            print("Length quality:", get_summary_length(numsum_list_[i]))    
                            print("Simplicity:", get_simplicity(numsum_list_[i]+1))
                            print()
                                                                
                            if "WIT" not in summary_dict.keys():
                                summary_dict["WIT"] = sub_dict
                            else:
                                for key in sub_dict:
                                    if key in summary_dict["WIT"].keys() and treatment in summary_dict["WIT"][key].keys():
                                        summary_dict["WIT"][key][treatment] += 1
                                    else:
                                        if key not in summary_dict["WIT"].keys():
                                            summary_dict["WIT"][key] = dict()
                                        summary_dict["WIT"][key][treatment] = 1 
                    
                    # Multivariate general if-then pattern summaries
                    sub_dict = dict()
                    if tw > 0 and attr != "MyFitnessPalMeals":
                        summarizer_type = "Past Daily TW - Generalized If-Then "
                        for i in range(len(key_list)):
                            if key_list[i] == "step count":
                                key_list[i] = "Step Count"    
                            elif key_list[i] == "heart rate":
                                key_list[i] = "Heart Rate"
                            
                                
                            summarizer_type += key_list[i]
                        
                            if i != len(key_list)-1:
                                summarizer_type += " and " 
                                
                        summarizers = ["very low","low","moderate","high","very high"]
                        if alpha_size == 7:
                            summarizers = summarizer_7                            
                        summarizer_list = []
                        for i in range(len(key_list)):
                            if key_list[i] == "Heart Rate" or key_list[i] == "heart rate":
                                summarizer_list.append(hr_summarizers)                                 
                            else:
                                summarizer_list.append(summarizers)      
                        
                        key_combos = []
                        for i in range(len(key_list)):
                            key_comb = combinations(key_list,i+1)
                            key_combos.append(list(key_comb))  
                        
                        for key_combo in key_combos:
                            for flag_ in key_combo:
                                flag_ = list(flag_)          
                                
                                avg_list, t1_list, quantifier_list, summary_list, summarizers = generate_summaries(summarizer_list,summarizer_type,key_list,sax_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,xval="days",flag=flag_)
                                if quantifier_list != None:
                                    quantifier_list = [quantifier for quantifier in quantifier_list if quantifier == "all of the"]
                                    if len(quantifier_list) != 0:
                                        index = best_quantifier_index(quantifier_list,t1_list)
                                        summary = summary_list[index]
                                        summarizers = summarizers[index]
                                        truth = t1_list[index]
                                        
                                        if summary not in sub_dict.keys():
                                            sub_dict[summary] = dict()
                                            
                                        if attr == "StepUp":
                                            treatment = df_list["Treatment"][0]
                                            if treatment not in sub_dict[summary].keys():
                                                sub_dict[summary][treatment] = 1
                                            else:
                                                sub_dict[summary][treatment] += 1                                               
                                
                                        print("General if-then pattern summary:", summary)
                                        print("Truth value:", truth)
                  
                                        query_ = [["qualifier",flag_,summarizers,alphabet_list]]
                                        flag = None
                                        if "Heart Rate" in key_list:
                                            flag = "HR"
                                        t3, coverage = degree_of_covering(key_list,sax_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag)
                                        t4 = degree_of_appropriateness(key_list,sax_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag=flag)
                                     
                                        length = get_summary_length(len(summarizers))
                                        simplicity = get_simplicity(len(flag_)+len(summarizers))
                                        t2 = degree_of_imprecision(avg_list)
                                        print("Imprecision:",t2)
                                        print("Covering:",t3)                                            
                                        print("Appropriateness:", t4)
                                        print("Relevance:", coverage)
                                        print("Length quality:", length)
                                        print("Simplicity:", simplicity)
                                        print() 
                                        proto_cnt += 1  
                                        
                                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                            with open(arm_filepath,"a",newline='') as csvfile:
                                                pid = pid_list[df_index]
                                                datawriter = csv.writer(csvfile)
                                                key_list_str = ""
                                                summ_str = ""
                                                flag_str = ""
                                                q_str = ""
                                                index_list = []
                                                for j in range(len(key_list)):
                                                    if key_list[j] in flag_:
                                                        continue
                                                    
                                                    key_list_str += key_list[j]
                                                    index_list.append(j)
                                                    if j != len(key_list)-1:
                                                        key_list_str += ", "
                                                  
                                                        
                                                for j in range(len(flag_)):
                                                    flag_str += flag_[j]
                                                    j_ = key_list.index(flag_[j])
                                                    index_list.append(j_)
                                                    if j != len(flag_)-1:
                                                        flag_str += ", "      
                                                        
                                                for j in range(len(index_list)):
                                                    index_ = index_list[j]
                                                    summ_str += summarizers[index_]
                                                    if j != len(index_list)-1:
                                                        summ_str += ", "    
                                                        
                                                datawriter.writerow([pid,key_list_str.strip(', ')+"|"+flag_str.strip(', '),tw,'GIT',quantifier_list[index],summ_str,flag_str])                                               
                        if "GIT" not in summary_dict.keys():
                            summary_dict["GIT"] = sub_dict
                        else:
                            for key in sub_dict:
                                if key in summary_dict["GIT"].keys() and treatment in summary_dict["GIT"][key].keys():
                                    summary_dict["GIT"][key][treatment] += 1
                                else:
                                    if key not in summary_dict["GIT"].keys():
                                        summary_dict["GIT"][key] = dict()
                                    summary_dict["GIT"][key][treatment] = 1     

                # Multivariate day-based pattern summaries
                sub_dict = dict()
                weekdays = list(set(date_column))
                for weekday in weekdays:
                    if TW == "hours":
                        break
                    
                    summarizer_type = "Day-based pattern summary - " 
                    for i in range(len(key_list)):
                        if key_list[i] == "step count":
                            key_list[i] = "Step Count"    
                            
                        summarizer_type += key_list[i]
                        if i != len(key_list)-1:
                            summarizer_type += " and "              
                  
                    weekday_data_list = []
                    weekday_index_list = []
                    day_summ_list = []
                    day_summarizers = ["very low","low","moderate","high","very high"]
                    if alpha_size == 7:
                        day_summarizers = summarizer_7                        
                    for j in range(len(key_list)):
         
                        if key_list[j] == "Heart Rate" or attr == "MyFitnessPalMeals":
                            weekday_data = [data[k] for k in range(len(date_column)) if date_column[k] == weekday]
                        elif attr == "Activity":
                            full_day_sax = ""
                            for day in day_list:
                                full_day_sax += data_dict[day]
                            weekday_data = [full_day_sax[k] for k in range(len(date_column)) if date_column[k] == weekday]
                        else:
                            weekday_data = [sax_list[j][k] for k in range(len(date_column)) if date_column[k] == weekday]
                        weekday_indices = [k for k in range(len(date_column)) if date_column[k] == weekday]
                        
                        weekday_data_list.append(weekday_data)
                        weekday_index_list.append(weekday_indices)
                        
                        if key_list[j] == "Heart Rate" or key_list[j] == "heart rate":
                            key_list[j] = "Heart Rate"
                            day_summ_list.append(hr_summarizers)
                        elif attr == "MyFitnessPalMeals":
                            day_summ_list = [carb_summarizers]
                        else:
                            day_summ_list.append(day_summarizers)
                    
                    avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(day_summ_list,summarizer_type,key_list,weekday_data_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,xval=weekday)
                    if summary_list != None:
                        index = best_quantifier_index(quantifier_list,t1_list)
                        day_summary = summary_list[index]
                        summarizers = summarizer_list[index]
                        truth = t1_list[index]          
                        average = avg_list[index]
                        
                        if day_summary not in sub_dict.keys():
                            sub_dict[day_summary] = dict()

                        if attr == "StepUp":
                            treatment = df_list["Treatment"][0]
                            if treatment not in sub_dict[day_summary].keys():
                                sub_dict[day_summary][treatment] = 1
                            else:
                                sub_dict[day_summary][treatment] += 1                             
                        
                        print("Day-based pattern summary:", day_summary)
                        print("Truth value:", truth)

                        indices = [index for index in weekday_indices]
    
                        query_ = [["current index", indices]]
                        flag_ = None
                        if attr == "Heart Rate":
                            flag_ = "HR"

                        t3, coverage = degree_of_covering(key_list,sax_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag_)
                        t4 = degree_of_appropriateness(key_list,sax_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag=flag_)
                        length = get_summary_length(len(summarizers))
                        simplicity = get_simplicity(len(summarizers)+1)
                        t2 = degree_of_imprecision(avg_list)
                        print("Imprecision:",t2)
                        print("Covering:",t3)                            
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1 
                        
                        if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                            with open(arm_filepath,"a",newline='') as csvfile:
                                pid = pid_list[df_index]
                                datawriter = csv.writer(csvfile)
                                key_list_str = ""
                                summ_str = ""
                                flag_str = ""
                                q_str = ""
                                index_list = []
                                for j in range(len(key_list)):
                                    
                                    key_list_str += key_list[j]
                                    index_list.append(j)
                                    if j != len(key_list)-1:
                                        key_list_str += ", "
                                                                                                      
                                for j in range(len(summarizers)):
                                    summ_str += summarizers[j]
                                    if j != len(summarizers)-1:
                                        summ_str += ", "    
                                        
                                datawriter.writerow([pid,key_list_str+'|'+weekday,tw,'DB',quantifier_list[index],summ_str,weekday])                              
                                 
                if "DB" not in summary_dict.keys():
                    summary_dict["DB"] = sub_dict
                else:
                    for key in sub_dict:
                        if key in summary_dict["DB"].keys() and treatment in summary_dict["DB"][key].keys():
                            summary_dict["DB"][key][treatment] += 1
                        else:
                            if key not in summary_dict["DB"].keys():
                                summary_dict["DB"][key] = dict()
                            summary_dict["DB"][key][treatment] = 1   
                            
                # Goal assistance summary
                sub_dict = dict()
                if tw > 0 and attr != "MyFitnessPalMeals":
                    last_weeks = dict()
                    for key in key_list:
                        if key != "date" and key != "ActivFit":
                            tmp = key.split(" ")
                            key_str = ""
                            for i in range(len(tmp)):
                                key_str += tmp[i].capitalize()
                                if i != len(tmp)-1:
                                    key_str += " "
                            
                            if key == "Calorie Intake":
                                last_weeks[key] = sum(list(df_list["Calories"][start_day:end_day]))/float(tw)
                            else:
                                try:   
                                    key = key_str.replace(" Intake","s")     
                                    if key == "Step Count":
                                        key = "Step Count"
                                    if key == "Stock Market Data":
                                        key = "close value"  
                                    if key == "Average Temperature":
                                        key = "Average Temperature"
                                      
                                    last_weeks[key] = sum(list(df_list[key][start_day:end_day]))/float(tw)
                                except KeyError:
                                    key = key_str.replace(" Intake","") 
                                    if key == "Step Count":
                                        key = "Step Count"        
                                    if key == "Close Value":
                                        key = "close value"
                                    if key == "Aapl Close Value":
                                        key = "AAPL close value"
                                    if key == "Aet Close Value":
                                        key = "AET close value" 
                                    if key == "Alabama Temperature":
                                        key = "Alabama temperature"                                        
                                    if key == "Alaska Temperature":
                                        key = "Alaska temperature"
                                    last_weeks[key] = sum(list(df_list[key][start_day:end_day]))/float(tw)                        
                            
                    goal_dict = goal_assistance("2000-cal",last_weeks)
                    num_summarizers = len(goal_dict.keys())
                    if goal_dict and num_summarizers>0:
                        summary = get_protoform("Goal Assistance",list(goal_dict.keys()),None,list(goal_dict.values()),qualifier_info=["2000-calorie diet"])
                        if summary != "":
                            if summary not in sub_dict.keys():
                                sub_dict[summary] = dict()
                                
                            if attr == "StepUp":
                                treatment = df_list["Treatment"][0]
                                if treatment not in sub_dict[summary].keys():
                                    sub_dict[summary][treatment] = 1
                                else:
                                    sub_dict[summary][treatment] += 1                                
                            print("Goal assistance summary:", summary)
                            length = get_summary_length(num_summarizers)
                            simplicity = get_simplicity(num_summarizers)
                            print()
                            
                            proto_cnt += 1
                            
                            if attr == "MyFitnessPal" or attr in ["Calorie Intake","Carbohydrate Intake"] or attr == "StepUp" or attr == "Step Count":
                                with open(arm_filepath,"a",newline='') as csvfile:
                                    pid = pid_list[df_index]
                                    datawriter = csv.writer(csvfile)
                                    key_list_str = ""
                                    summ_str = ""
                                    flag_str = ""
                                    q_str = ""
                                    index_list = []
                                    for j in range(len(key_list)):
                                        
                                        key_list_str += key_list[j]
                                        try:
                                            if key_list[j] == "Carbohydrate Intake":
                                                summ_str += goal_dict["Carbohydrates"]
                                            else:
                                                summ_str += goal_dict[key_list[j]]
                                        except KeyError:
                                            if j != len(key_list)-1:
                                                key_list_str += ", "                                                
                                            continue
                                        
                                        if j != len(key_list)-1:
                                            key_list_str += ", "
                                            summ_str += ", "   
                                            
                                    datawriter.writerow([pid,key_list_str,tw,'GA',None,summ_str,None])                                
                                                              
                            if "GA" not in summary_dict.keys():
                                summary_dict["GA"] = sub_dict
                            else:
                                for key in sub_dict:
                                    if key in summary_dict["GA"].keys() and treatment in summary_dict["GA"][key].keys():
                                        summary_dict["GA"][key][treatment] += 1
                                    else:
                                        if key not in summary_dict["GA"].keys():
                                            summary_dict["GA"][key] = dict()
                                        summary_dict["GA"][key][treatment] = 1               
      
                                
    print("Number of summaries produced:", proto_cnt)
    if proto_cnt > 0:
        user_cnt += 1
    all_cnt += proto_cnt
    print()
    print()
    proto_cnt = 0
                
print("done")
print(all_cnt)
print(user_cnt)

        
