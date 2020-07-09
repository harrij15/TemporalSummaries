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
    attr_index = 1 # Chooses the attribute in attributes list
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
    path = "C:/Users/harrij15/Documents/GitHub/TemporalSummaries//" # Path for pattern data
    cygwin_path = r"C:\Apps\cygwin64\bin" # Path to Cygwin    
        
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
                            prev_start_day = None
                            tw_sax = None
                                                                                
                        summary_data = full_sax_rep[start_day:end_day]
                    else: 
                        summary_data = full_sax_rep[start_day:end_day]
                        x_vals = "days"          
                                                                             
                    sax_list.append(full_sax_rep)  
                    summary_data_list.append(summary_data)
                
                if error:
                    continue
                                
                # Multivariate standard evaluation summaries (TW granularity)                     
                tw_summary, t3, coverage, t4, length, simplicity, first = generateSETW(attr,key_list,pid_list,singular_TW,past_full_wks,tw_sax_list,letter_map_list,alpha_sizes,tw,tw_sax,age=age,activity_level=activity_level)
                if tw_summary != None:
                    print("Overall " + singular_TW + " summary (" + first.lower() + "granularity):", tw_summary)
                    print("Covering:", t3)
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print()
                    proto_cnt += 1                   
                            
                # Multivariate standard evaluation summaries (sTW granularity)
                past_tw_list = [sax[start_day:end_day] for sax in sax_list]
                daily_summary, truth, t2, t3, coverage, t4, length, simplicity = generateSESTW(attr,key_list,past_tw_list,letter_map_list,alpha,alpha_sizes,TW,start_day=start_day,end_day=end_day,age=age,activity_level=activity_level)
                
                if daily_summary != None:
                    print("Day summary (daily granularity):", daily_summary)
                    print("Truth value:", truth)
                    print("Imprecision:", t2)
                    print("Covering:", t3)
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print()
                    proto_cnt += 1
                            
                # Multivariate standard evaluation summary with specified qualifier (sTW)
                if key_list[i] == "Activity":
                    past_tw_list = [day_sax]
                else:
                    past_tw_list = [sax[start_day:end_day] for sax in sax_list]
                      
                summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, flag_ = generateSESTWQ(attr,key_list,past_tw_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,TW,age,activity_level)
                if summaries != None:
                    for j in range(len(summaries)):
                        
                        summary = summaries[j]
                        truth = truth_list[j]
                        t2 = t2_list[j]
                        t3 = t3_list[j]
                        coverage = coverage_list[j]
                        t4 = t4_list[j]
                        length = length_list[j]
                        simplicity = simplicity_list[j]
                        
                        print("Overall " + singular_TW + " summary w/ ",end="")
                        for i in range(len(flag_)):
                            print(flag_[i],end="")
                            if i != len(flag_)-1:
                                print(" and ",end="")
                        print(" qualifier (daily granularity): " +  summary)
                        print("Truth value:", truth)
                        print("Imprecision:",t2)
                        print("Covering:",t3)
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print()
                        proto_cnt += 1   
                            
                # Multivariate evaluation comparison summaries           
                comparison_summary, t3, coverage, t4, length, simplicity = generateEC(attr,key_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,age=age,activity_level=activity_level)
                if comparison_summary != None:
                    print("Standard evaluation comparison summary (" + singular_TW + "ly granularity): " + comparison_summary)
                    print("Covering:",t3)                                
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print() 
                    proto_cnt += 1            
                     
                # Multivariate goal comparison summaries
                comparison_summary, t3, coverage, t4, length, simplicity = generateGC(attr,attr_list,key_list,data_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,prev_start_day,start_day,end_day,age=age,activity_level=activity_level)
                if comparison_summary != None:
                    
                    if singular_TW == "day":
                        print("Goal comparison summary (daily granularity): " + comparison_summary)
                    else:
                        print("Goal comparison summary (" + singular_TW + "ly granularity): " + comparison_summary)
                     
                    print("Covering:",t3)                                
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print()   
                    proto_cnt += 1   

                # Goal evaluation summaries
                past_tw_list = []
                for i in range(len(key_list)):
                    if key_list[i] == "Activity":
                        continue
                    else:
                        past_tw_list.append(data_list[i][start_day:end_day])
                        
                goal_summary, truth, t2, t3, coverage, t4, length, simplicity = generateGE(attr,attr_list,key_list,sax_list,past_tw_list,letter_map_list,alpha,alpha_sizes,TW,start_day=start_day,end_day=end_day,age=age,activity_level=activity_level)    
                if goal_summary != None:
                   
                    print("Goal evaluation summary:", goal_summary)
                    print("Truth value:", truth)
                    print("Imprecision:",t2)
                    print("Covering:",t3)                            
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print() 
                    proto_cnt += 1  

                # Standard trends summaries
                trend_summary, truth, t2, t3, coverage, t4, length, simplicity = generateST(attr,key_list,data_list,letter_map_list,alpha_sizes,alpha,TW,age,activity_level)
                if trend_summary != None:
                    print("Standard trend summary:", trend_summary)
                    print("Truth value:", truth)
                    print("Imprecision:",t2)
                    print("Covering:",t3)                        
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print() 
                    proto_cnt += 1      
                        
                # Multivariate cluster-based pattern summaries
                cluster_summary, truth, t2, t3, coverage, t4, length, simplicity, tw_index, cluster_data = generateCB(attr,key_list,full_sax_rep,tw_sax_list,sax_list,data_list,letter_map_list,alpha_sizes,alpha,tw,TW,age,activity_level)
                if cluster_summary != None:
                    print("Cluster-based pattern summary:", cluster_summary)
                    print("Truth value:", truth)
                    print("Imprecision:",t2)
                    print("Covering:",t3)                                
                    print("Appropriateness:", t4)
                    print("Relevance:", coverage)
                    print("Length quality:", length)
                    print("Simplicity:", simplicity)
                    print() 
                    proto_cnt += 1 
                            
                    # Multivariate standard pattern summaries
                    sp_summary, t3, coverage, t4, length, simplicity = generateSP(key_list,cluster_data,tw_index)
                    if sp_summary != None:
                        
                        print("Standard pattern summary:", sp_summary)
                        print("Covering:",t3)                            
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1              
                                
                # Multivariate if-then pattern summaries
                summary_list, t3_list, t4_list, coverage_list, length_list, simplicity_list, weekday_summaries, t3_list_, t4_list_, coverage_list_, length_list_, simplicity_list_, proto_cnt = generateIT(attr,key_list,sax_list,alphabet_list,letter_map_list,tw,weekday_dict,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,date_column,age,activity_level)
                    
                if summary_list != None:
                    print("If-then pattern summaries")
                    
                    for i in range(len(summary_list)):
                        print(summary_list[i])
                        print("Covering:",t3_list[i])                                
                        print("Appropriateness:", t4_list[i])
                        print("Relevance:", coverage_list[i])
                        print("Length quality:", length_list[i])
                        print("Simplicity:", simplicity_list[i])
                        print()  
                              
                print()
                    
                if weekday_summaries != None:
                    for i in range(len(weekday_summaries)):
                        print(weekday_summaries[i])
                        print("Covering:",t3_list_[i]) 
                        print("Appropriateness:", t4_list_[i])
                        print("Relevance:", coverage_list_[i])                   
                        print("Length quality:", length_list_[i])    
                        print("Simplicity:", simplicity_list_[i])
                        print()
                                                            
                         
                # Multivariate general if-then pattern summaries\
                summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list = generateGIT(attr,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level)
                
                if summaries != None:
                    for i in range(len(summaries)):
                        print("General if-then pattern summary:", summary)
                        print("Truth value:", truth)
                        print("Imprecision:",t2)
                        print("Covering:",t3)                                            
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        proto_cnt += 1  
                            
                # Multivariate day-based pattern summaries       
                summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list = generateDB(attr,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column)
                if summaries != None:
                    for i in range(len(summaries)):
                        print("Day-based pattern summary:", summaries[i])
                        print("Truth value:", truth_list[i])
                        print("Imprecision:",t2_list[i])
                        print("Covering:",t3_list[i])                            
                        print("Appropriateness:", t4_list[i])
                        print("Relevance:", coverage_list[i])
                        print("Length quality:", length_list[i])
                        print("Simplicity:", simplicity_list[i])
                        print() 
                        proto_cnt += 1                                                     
                            
                # Goal assistance summary  
                summary, length, simplicity = generateGA(attr,df_list,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column)
                if summary != None:
                    print("Goal assistance summary:", summary)
                    print()
                    proto_cnt += 1            
      
                                
    print("Number of summaries produced:", proto_cnt)
    if proto_cnt > 0:
        user_cnt += 1
    all_cnt += proto_cnt
    print()
    proto_cnt = 0
                
print(all_cnt)
print(user_cnt)

        
