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
    attr_index = -1 # Chooses the attribute in attributes list
    age = 23
    activity_level = "active"   
    alpha_size = 5
    alpha = 0.9 # For alpha cut 
    all_cnt = 0
    user_cnt = 0
    ada_goal = None
    arm_dict = dict()
    provenance = True
    
    # Parameters for SPADE
    min_conf = 0.8
    min_sup = 0.2
    treatment = None
    path = "C:/Users/harrij15/Documents/GitHub/TemporalSummaries//" # Path for pattern data
    cygwin_path = r"C:\Apps\cygwin64\bin" # Path to Cygwin    
    arm_filepath = "data/ArmsMFP/arms.csv"
        
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
    
    sax_to_summ_5 = {"a" : "very low",
                     "b" : "low",
                     "c" : "moderate",
                     "d" : "high",
                     "e" : "very high"}    
    
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
    elif attr == "Arm Comparison":
        df_index_list = [0]
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
    pid_list = list(range(len(df_lists[0])-1))
    
    summary_dict = dict()
    df_index = -1
    for df_list in df_lists:
        df_index += 1
        
        if attr == "Arm Comparison":
            
            group_dict = {"0" : "Treatment0",
                          "1" : "Treatment1",
                          "2" : "Treatment2",
                          "c" : "Control"}
            if df_list["group"] != None:
                if "cluster" in df_list["group"]:
                    group = df_list["group"]
                else:
                    group = group_dict[df_list["group"]]
            else:
                group = ''
                
            #proto_type = list(set(df_list["Protoform Type"]))
            summarizers_dict = {"Goal" : "reached"}
            attribute_list = df_list["Attribute"]
            time_window = df_list["Time Window"][0]
            proto_list = df_list["Protoform Type"]
            qualifier_list = df_list["Qualifier"]
            #input(qualifier_list)
            
            items = []
            for i in range(len(attribute_list)):
                sub_list = [attribute_list[i],proto_list[i],qualifier_list[i]]
                if type(sub_list[-1]) != str:
                    sub_list[-1] = None
                items.append(sub_list)
            #items = list(set(df_list["Attribute"]))
            #input(items)
            past_items = []
            for item in items:
                #input([item,past_items,item in past_items])
                repeat = False
                for item_ in past_items:
                    #print(item,past_items)
                    try:
                        diff = False
                        for i in range(len(item)):
                            #print(item[i],item_[i])
                            import math
                            if item[i] != item_[i]:#or (math.isnan(item[i]) and math.isnan(item_[i].isnan())):
                                diff = True
                                break
                            
                        repeat = not diff
                        
                    except IndexError:
                        repeat = True 
                      
                    
                    if repeat:
                        break
                    #if item == item_.join():
                        
                        #repeat = True
                        #break
                #input(repeat)  
                if repeat:
                    continue
                else:
                    past_items.append(item)
                
                
                attribute = item[0]
                proto_type = item[1]
                qualifier = item[2]
                if attribute in summarizers_dict:
                    summarizer = summarizers_dict[attribute]
                    summarizers_list = ["none of the","almost none of the","some of the","half of the","more than half of the","most of the","all of the"]
                else:
                    summarizer = ''
                    summ_set = set([])
                    summs = df_list["Summarizer"]
                    total_summ = []
                    for i in range(len(summs)):
                        if attribute_list[i] == attribute and proto_list[i] == proto_type:
                            summ_set.add(summs[i])
                            total_summ.append(summs[i])
                    summarizers_list = list(summ_set)
                    
                    quant_set = set([])
                    quants = df_list["Quantifier"]
                    total_quant = []
                    for i in range(len(quants)):
                        if attribute_list[i] == attribute and proto_list[i] == proto_type:
                            quant_set.add(quants[i])
                            total_quant.append(quants[i])
                    quantifiers_list = list(quant_set)
                
                #print(attribute)
                #input(summarizers_list)
                summarizer_type = "Arm Comparison"
                key_list = ["Arm Comparison"]
                letter_map_list = [[]]
                alpha_sizes = [[]]
                alpha = None
                if "Quantifier (Goal)" in df_list.keys():
                    data_list = [df_list["Quantifier (Goal)"]]
                elif df_list["Quantifier"][0] == None or proto_type == "SETW":
                    data_list = [total_summ]
                else: 
                    data_list = []
                    for i in range(len(total_summ)):
                        data_list.append([total_summ[i],total_quant[i]])
                    data_list = [data_list]
                    
                    matrix_list = []
                    
                    for i in range(len(summarizers_list)):
                        for j in range(len(quantifiers_list)):
                            matrix_list.append([summarizers_list[i],quantifiers_list[j]])
                            
                    summarizers_list = matrix_list
                   
                    
                
                #input(data_list)
                #print(summarizers_list,data_list)
                #input(len(summarizers_list))
                avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries([summarizers_list],summarizer_type,key_list,data_list,letter_map_list,alpha_sizes,alpha,TW=TW,flag=[group,summarizer,proto_type,attribute,qualifier,time_window])
                if quantifier_list != None:
                    #input(quantifier_list)
                    index = best_quantifier_index(quantifier_list,t1_list)
                    arm_summary = summary_list[index]
                    summarizer_list = summarizer_list[index]
                    truth = t1_list[index]
                    avg = avg_list[index]
                    
                    #print(summarizer_list)
                    summ_cnt = 0
                    for item in summarizer_list:
                        tmp = item
                        if type(item) is list:
                            tmp = item[0]
                        #print(tmp)
                        if '_' in tmp:
                            tmp_ = tmp.split('_')
                            tmp_ = [x for x in tmp_ if len(x)>0]
                            #print(tmp_)
                            summ_cnt += len(tmp_)
                        elif ',' in tmp:
                            tmp_ = tmp.split(',')
                            tmp_ = [x for x in tmp_ if len(x)>0]   
                            #print(tmp_)
                            summ_cnt += len(tmp_)                            
                        else:
                            summ_cnt += 1
                    #print(summ_cnt)                                
                    #output_info
                    #print([summarizer_list[0],quantifier_list[index]])
            
                    if arm_summary != None:
                        print("Arm comparison summary ("+proto_type+"):", arm_summary)
                        #print("Percentage:",avg)
                        print("Truth value:", truth)
                        
                        length = get_summary_length(summ_cnt)
                        simplicity = get_simplicity(summ_cnt+1)
                        t3, coverage = degree_of_covering(key_list,data_list,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level)
                        t4 = degree_of_appropriateness(key_list,data_list,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)
                        t2 = degree_of_imprecision(avg_list)
                        print("Imprecision:",t2)
                        print("Covering:",t3)                        
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        #if proto_type == "GIT":
                        #input()
                        proto_cnt += 1
       
        else:
        
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
            pid = pid_list[df_index]
        
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
                        
                    if len(key_list) != 2:
                        continue
                    
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
                    
                    heat_map_list = []
                    #print(sax_list)
                    for i in range(len(sax_list)):
                        heat_map = dict()
                        #print(sax_list)
                        for j in range(alpha_sizes[i]):
                            if attr == "Heart Rate":
                                heat_map[hr_alphabet[j]] = {'min' : float('Inf'), 'max' : 0}
                            else:
                                heat_map[alphabet[j]] = {'min' : float('Inf'), 'max' : 0}                            
                        i_ = -1
                        if len(key_list) > 1:
                            i_ = i     
                        #print(sax_list[i])
                        #input(data_list)
                        for j in range(len(sax_list[i])):
                            letter = sax_list[i][j]
                            value = data_list[i_][j]
                            #print(letter,value)
                            
                            if value < heat_map[letter]['min']:
                                heat_map[letter]['min'] = value
                            if value > heat_map[letter]['max']:
                                heat_map[letter]['max'] = value 
                                
                        heat_items = list(heat_map.items())
                        for j in range(len(heat_items)):
                            letter = heat_items[j][0]
                            pair = heat_items[j][1]
                            
                            letter_index = alphabet.index(letter)
                            
                            try:
                                prev_letter = alphabet[letter_index-1]
                                prev_diff = abs(heat_map[prev_letter]['max'] - heat_map[letter]['min'])
                            except KeyError:
                                prev_diff = 0.5
                            
                            try:
                                next_letter = alphabet[letter_index+1]
                                next_diff = abs(heat_map[next_letter]['min'] - heat_map[letter]['max'])   
                            except KeyError:
                                next_diff = 0.5                            
                            
                            if pair['min'] == pair['max']:
                                heat_map[letter]['min'] = pair['min']-min(0.5,prev_diff)
                                heat_map[letter]['max'] = pair['max']+min(0.5,next_diff)
                                
                                
                        heat_map_list.append(heat_map)                      
                    
                    if error:
                        continue
                                       
                    if provenance:
                        for i in range(len(key_list)):
                            i_ = -1
                            if len(key_list) > 1:
                                i_ = i
                            show_provenance([key_list[i]],[data_list[i_]],tw,[heat_map_list[i]],hours=(tw==0.04))                    
                    #input(heat_map_list)
                                    
                    # Multivariate standard evaluation summaries (TW granularity)                     
                    tw_summary, t3, coverage, t4, length, simplicity, first, tw_summarizers = generateSETW(attr,key_list,pid_list,singular_TW,past_full_wks,tw_sax_list,letter_map_list,alpha_sizes,tw,tw_sax,age=age,activity_level=activity_level,arm_filepath=arm_filepath)
                    if tw_summary != None:
                        print("Overall " + singular_TW + " summary (" + first.lower() + "granularity):", tw_summary)
                        print("Covering:", t3)
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print()
                        
                        if provenance:
                            for i in range(len(key_list)):
                                tmp = build_heatmap(heat_map_list[i],tw_summary,[tw_summarizers[i]],alpha_sizes[i])
                                #input(summarizers)
                                # SETW data chart
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i           
                                
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=[start_day],hours=(tw==0.04))                        
                        
                        proto_cnt += 1                   
                                
                    # Multivariate standard evaluation summaries (sTW granularity)
                    past_tw_list = [sax[start_day:end_day] for sax in sax_list]
                    start_day_ = 0
                    end_day_ = tw
                    if tw <= 0.04:
                        end_day_ = len(full_sax_rep)
                    daily_summary, truth, t2, t3, coverage, t4, length, simplicity, summarizers = generateSESTW(attr,key_list,past_tw_list,letter_map_list,alpha,alpha_sizes,TW,start_day=0,end_day=end_day_,age=age,activity_level=activity_level,arm_filepath=arm_filepath)
                    
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
                        
                        if provenance:
                            res = []
                            #input(key_list)
                            for i in range(len(key_list)):
                                if key_list[i] == "Heart Rate":
                                    res.append([x+start_day for x in range(len(full_sax_rep[start_day:end_day])) if full_sax_rep[start_day:end_day][x] == summarizer_to_SAX(summarizers[i],alpha_sizes[i],attr=attr)])
                                else:
                                    res.append([x+start_day for x in range(len(sax_list[i][start_day:end_day])) if sax_list[i][start_day:end_day][x] == summarizer_to_SAX(summarizers[i],alpha_sizes[i],attr=attr)])
                            #print(res)
                            for i in range(len(key_list)):
                                tmp = build_heatmap(heat_map_list[i],daily_summary,[summarizers[i]],alpha_sizes[i])                
                                # SESTW data chart
                                #if len(key_list) == 1:
                                #print(res[i])
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i     
                                #input(start_day)
                                rgn_idx = start_day
                                if attr == "WeatherHourly":
                                    rgn_idx = None
                                
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=res[i],multicolor=True,single_day=True,region_index=rgn_idx,hours=(tw==0.04))                        
                        proto_cnt += 1
                                
                    # Multivariate standard evaluation summary with specified qualifier (sTW)
                    if key_list[i] == "Activity":
                        past_tw_list = [day_sax]
                    else:
                        past_tw_list = [sax[start_day:end_day] for sax in sax_list]
                    
                    summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, flag_, summarizers_list = generateSESTWQ(attr,key_list,past_tw_list,summarizer_7,start_day_,end_day_,alpha,alpha_sizes,letter_map_list,alphabet_list,TW,age,activity_level,arm_filepath=arm_filepath)
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
                            
                            if provenance:
                                    letters = []
                                    for i in range(len(summarizers_list)):
                                        summarizer = summarizers_list[0][i]
                                        #print(summarizers_list)
                                        #print(summarizers_list)
                                        letters.append(summarizer_to_SAX(summarizer,alpha_sizes[i],attr=attr))                                    
                                    
                                    res = []
                                    for i in range(len(past_tw_list[0])):
                                        result = True
                                        #print(letters)
                                        for j in range(len(letters)):
                                            result = result and (letters[j] == past_tw_list[j][i])
                                            #print(letters[j],past_tw_list[j][i])
                                        
                                        #print(result)    
                                        if result:
                                            #print(i,start_day)
                                            res.append(start_day+i)
                                    
                                    #input(res)
                                    for i in range(len(key_list)):
                                        tmp = build_heatmap(heat_map_list[i],summary,[summarizers_list[0][i]],alpha_sizes[i])
                                        #input(heat_map_list[i])
                                        #print(data_list)
                                        #input(start_day)
                                        rgn_idx = start_day
                                        if tw == 0.04:
                                            rgn_idx = None
                                        # SESTWQ data chart
                                        i_ = -1
                                        if len(key_list) > 1:
                                            i_ = i                
                                        #input(res)
                                        show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=res,multicolor=True,single_day=True,region_index=rgn_idx,hours=(tw==0.04))
                                    #input()
                                    proto_cnt += 1
                                    break
                               
                                
                    # Multivariate evaluation comparison summaries           
                    comparison_summary, t3, coverage, t4, length, simplicity = generateEC(attr,key_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,age=age,activity_level=activity_level,arm_filepath=arm_filepath)
                    if comparison_summary != None:
                        print("Standard evaluation comparison summary (" + singular_TW + "ly granularity): " + comparison_summary)
                        print("Covering:",t3)                                
                        print("Appropriateness:", t4)
                        print("Relevance:", coverage)
                        print("Length quality:", length)
                        print("Simplicity:", simplicity)
                        print() 
                        
                        if provenance:
                            try:
                                first_index_ = tw*(len(tw_sax_list[0])-2)
                                second_index_ = tw*(len(tw_sax_list[0])-1)
                            except IndexError:
                                first_index_ = len(full_sax_rep)-1
                                second_index_ = len(full_sax_rep)-2
                            
                            for i in range(len(key_list)):
                                tmp = [{}]
                                
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i         
                                    
                                if tw == 0.04:
                                    first_index_ = len(full_sax_rep)-1
                                    second_index_ = len(full_sax_rep)-2
                                                                        
                                #input([first_index_,second_index_])
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=[first_index_,second_index_],comparison=True,hours=(tw==0.04))                        
                        
                        proto_cnt += 1            
                         
                    # Multivariate goal comparison summaries
                    comparison_summary, t3, coverage, t4, length, simplicity = generateGC(attr,attr_list,key_list,data_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,prev_start_day,start_day,end_day,age=age,activity_level=activity_level,arm_filepath=arm_filepath)
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
                        
                        if provenance:
                            for i in range(len(key_list)):
                                tmp = [{}]
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i                                        
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=[prev_start_day,start_day],comparison=True,showgoal=True,hours=(tw==0.04))                          
                        
                        proto_cnt += 1   
    
                    # Goal evaluation summaries
                    past_tw_list = []
                    for i in range(len(key_list)):
                        if key_list[i] == "Activity":
                            continue
                        else:
                            past_tw_list.append(data_list[i][start_day:end_day])
                            
                    goal_summary, truth, t2, t3, coverage, t4, length, simplicity = generateGE(attr,attr_list,key_list,sax_list,past_tw_list,letter_map_list,alpha,alpha_sizes,TW,start_day=start_day,end_day=end_day,age=age,activity_level=activity_level,arm_filepath=arm_filepath)    
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
                        
                        if provenance:
                            for i in range(len(key_list)):
                                tmp = [{}]            
                                
                                # GE data chart
                                #if len(key_list) == 1:
                                goal = False
                                if key_list[i] == "Calorie Intake" or key_list[i] == "Heart Rate":
                                    goal = True
                                
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i                                    
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=[start_day],showgoal=goal,hours=(tw==0.04))                        
                        
                        proto_cnt += 1  
    
                    # Standard trends summaries
                    trend_summary, truth, t2, t3, coverage, t4, length, simplicity, trend_lists, summarizers = generateST(attr,key_list,data_list,letter_map_list,alpha_sizes,alpha,TW,age,activity_level,arm_filepath=arm_filepath)
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
                        
                        if provenance:
                            indices = []
                            for i in range(1,len(data)):
                                result = True
                                for j in range(len(summarizers)):
                                    summarizer = summarizers[j]
                                    value = trend_lists[j][i]                    
                                                            
                                    if summarizers[j] == "increases":
                                        result = result and (value > 0)
                                    elif summarizers[j] == "decreases":
                                        result = result and (value < 0)
                                    else:
                                        result = result and (value == 0)
                                
                                if result:
                                    indices.append(i-1)                                
                            
                            for i in range(len(key_list)):
                                tmp = [{}]            
                                
                                # ST data chart
                                
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i                                    
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=indices,multicolor=True,hours=(tw==0.04))                          
                        
                        proto_cnt += 1      
                            
                    # Multivariate cluster-based pattern summaries
                    cluster_summary, truth, t2, t3, coverage, t4, length, simplicity, tw_index, cluster_data, indices, clusters, summarizers = generateCB(attr,attr_list,key_list,full_sax_rep,tw_sax_list,sax_list,data_list,letter_map_list,alpha_sizes,alpha,tw,TW,age,activity_level,arm_filepath=arm_filepath)
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
                        
                        if provenance:
                            indices1 = []
                            for cluster in clusters:
                                if tw_index in cluster:
                                    indices1 = cluster
                                    break
                            indices1 = [x*tw for x in indices1]
                            week_indices_ = [int(x/7) for x in indices1]                                    
                            
                            for i in range(len(key_list)):
                                tmp = [{}]             
                                
                                summ_indices = []
                                for j in range(len(week_indices_)):
                                    #print(week_indices_[j])
                                    index = week_indices_[j]*tw
                                    if attr == "Heart Rate":
                                        letter_index = hr_alphabet.index(full_sax_rep[week_indices_[j]])
                                        summ = hr_sax_to_summ_5[full_sax_rep[week_indices_[j]]]
                                    else:
                                        letter_index = alphabet.index(tw_sax_list[i][week_indices_[j]])
                                        summ = sax_to_summ_5[tw_sax_list[i][week_indices_[j]]]
                                    summ_indices.append([index,letter_index,summ])   
                                    
                                    if week_indices_[j]+1 != len(tw_sax_list[i]):
                                        index += tw
                                        if attr == "Heart Rate":
                                            letter_index = hr_alphabet.index(full_sax_rep[week_indices_[j]+1])
                                            summ = hr_sax_to_summ_5[full_sax_rep[week_indices_[j]+1]]
                                        else:
                                            letter_index = alphabet.index(tw_sax_list[i][week_indices_[j]+1])
                                            summ = sax_to_summ_5[tw_sax_list[i][week_indices_[j]+1]]
                                        summ_indices.append([index,letter_index,summ])
                                                            
                                # CB data chart
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i                                        
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=indices1,region_index=tw_index*tw,summ_indices=summ_indices,hours=(tw==0.04))                         
                        
                        proto_cnt += 1 
                                
                        # Multivariate standard pattern summaries
                        sp_summary, t3, coverage, t4, length, simplicity = generateSP(attr,key_list,cluster_data,tw_index,indices,letter_map_list,alpha_sizes,age,activity_level,arm_filepath=arm_filepath)
                        if sp_summary != None:
                            
                            print("Standard pattern summary:", sp_summary)
                            print("Covering:",t3)                            
                            print("Appropriateness:", t4)
                            print("Relevance:", coverage)
                            print("Length quality:", length)
                            print("Simplicity:", simplicity)
                            print() 
                            
                            if provenance:
                                for i in range(len(key_list)):
                                    tmp = [{}]
                                    
                                    # SP data chart
                                    #if len(key_list) == 1:
                                    last_index = indices1[-1]
                                    if int(last_index/tw) == len(tw_sax_list[0])-1:
                                        last_index = indices1[-2]
                                        
                                    #print(int(last_index/tw),len(tw_sax_list)-1)
                                    for j in range(len(summ_indices)):
                                        if summ_indices[j][0] == last_index:
                                            summ_index = j
                                            break
                                    
                                    index = summ_indices[summ_index][0]+tw
                                    if attr == "Heart Rate":
                                        letter_index = hr_alphabet.index(full_sax_rep[int(index/tw)])
                                        summ = hr_sax_to_summ_5[hr_alphabet[letter_index]]
                                    else:
                                        letter_index = alphabet.index(tw_sax_list[i][int(index/tw)])
                                        summ = sax_to_summ_5[alphabet[letter_index]]                                 
                                    #letter_index = alphabet.index(tw_sax_list[i][int(index/tw)])
                                    #print(letter_index)
                                    #summ = sax_to_summ_5[alphabet[letter_index]]
                                    next_summ = [index,letter_index,summ]
                                    
                                    #print(summ_indices[summ_index],next_summ)
                                        
                                    #summ_index = math.ceil(last_index/tw)
                                    #print(summ_indices,len(summ_indices),summ_index,last_index)
                                    i_ = -1
                                    if len(key_list) > 1:
                                        i_ = i                                    
                                    show_provenance([key_list[i]],[data_list[i_]],tw,tmp,indices=[last_index],summ_indices=[summ_indices[summ_index],next_summ],hours=(tw==0.04))                            
                            
                            proto_cnt += 1              
                                    
                    # Multivariate if-then pattern summaries
                    summary_list, summarizers_list, t1_list, t2_list, t3_list, coverage_list, length_list, simplicity_list, weekday_summaries, summarizers_list_, t1_list_, t2_list_, t3_list_, coverage_list_, length_list_, simplicity_list_, proto_cnt = generateIT(attr,key_list,sax_list,alphabet_list,letter_map_list,tw,weekday_dict,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,date_column,age,activity_level,arm_filepath=arm_filepath)
                        
                    if summary_list != None:
                        print("If-then pattern summaries")
                        
                        for i in range(len(summary_list)):
                            print(summary_list[i])
                            print("Covering:",t3_list[i])                                
                            print("Relevance:", coverage_list[i])
                            print("Length quality:", length_list[i])
                            print("Simplicity:", simplicity_list[i])
                            print()  
                            
                            if provenance:
                                import copy
                                summarizers = copy.deepcopy(summarizers_list[i])
                                prefixes = summarizers[0]
                                suffixes = summarizers[1]
                                
                                #input([prefixes,suffixes])
                                #prefix_list = prefixes[0]
                                #suffix_list = suffixes[0]
                                
                                first_letters = []
                                second_letters = []
                                for j in range(len(prefixes)):
                                    #sublist = []
                                    substr = ''
                                    for k in range(len(prefixes[j])):
                                        #sublist.append(summarizer_to_SAX(prefixes[i][j],alpha_sizes[i]))
                                        substr += summarizer_to_SAX(prefixes[j][k],alpha_sizes[j],attr=attr)
                                    first_letters.append(substr)
                                    
                                for j in range(len(suffixes)):
                                    #sublist_ = []
                                    substr_ = ''
                                    for k in range(len(suffixes[j])):
                                        #sublist_.append(summarizer_to_SAX(suffixes[i][j],alpha_sizes[i]))   
                                        substr_ += summarizer_to_SAX(suffixes[j][k],alpha_sizes[j],attr=attr)
                                    second_letters.append(substr_)
                                
                                #print(first_letters,second_letters)
                                
                                letters_list = []
                                for j in range(len(first_letters)):
                                    letters_list.append(first_letters[j] + second_letters[j])
                                    
                                single_summ = [len(x) == 1 for x in letters_list]
                                                                
                                max_length = max([len(x) for x in letters_list])
                                index_ = 0
                                for j in range(len(letters_list)):
                                    diff = max_length - len(letters_list[j])
                                    if len(prefixes[j]) == 0:
                                        letters_list[j] = '*'*diff + letters_list[j] 
                                    else:
                                        letters_list[j] = letters_list[j] + '*'*diff
                                        
                                    #input(letters_list[j])
                                    
                                    if diff == 0:
                                        index_ = j
                                        
                                #for i in range(len(letters_list)):
                                    #if len(letters_list[i]) < max_l
                                #print(letters_list,index_)  
                                #print(sax_list[index_])
                                #print(sax_list[0])
        
                                if attr == "Heart Rate":
                                    res = [j for j in range(len(full_sax_rep)) if full_sax_rep.startswith(letters_list[index_],j)]
                                    res_ = [[] for j in range(1)]
                                else:
                                    res = [j for j in range(len(full_sax_rep)) if sax_list[index_].startswith(letters_list[index_],j)]
                                    res_ = [[] for j in range(len(sax_list))]
                                
                                for index_ in res:
                                    result = True
                                    info_ = []
                                    #input(letters_list)
                                    for j in range(len(sax_list)):
                                        candidate = ''
                                        length = 0
                                        while length < max_length and length < len(letters_list[j]) and letters_list[j][length] != '*':
                                            #print(length)
                                            candidate += letters_list[j][length]
                                            length += 1
                                        
                                            
                                        #input([candidate,length,max_length])
                                        
                                        
                                        #result = result and (letters_list[i].strip('*') in sax_list[i][index:index+max_length])
                                        #print(summary_list[i])
                                        #print(candidate,full_sax_rep[index_:index_+length])
                                        if attr == "Heart Rate":
                                            result = result and (candidate == full_sax_rep[index_:index_+length])
                                            info_.append([list(range(index_,index_+max_length)),letters_list[j],full_sax_rep[index_:index_+max_length]])
                                        else:
                                            result = result and (candidate == sax_list[j][index_:index_+length])
                                            info_.append([list(range(index_,index_+max_length)),letters_list[j],sax_list[j][index_:index_+max_length]])
                                        #print(list(range(index_,index_+max_length)),letters_list[j],sax_list[j][index_:index_+max_length])
                                        #info_.append([list(range(index_,index_+max_length)),letters_list[j],sax_list[j][index_:index_+max_length]])
                                        #input()
                                        #input([letters_list[i],sax_list[i][index:index+max_length]])
                                    #print(result)
                                    if result:
                                        #input(info_)
                                        for j in range(len(res_)):
                                            #print(info_[j][0])
                                            for k in range(len(info_[j][0])):
                                                #input([info_[j][1],info_[j][2],k])
                                                if info_[j][1][k] == info_[j][2][k] and info_[j][1][k] != '*' and info_[j][0][k] not in res_[j]:
                                                    #print(info_[i])
                                                    res_[j].append(info_[j][0][k])
                                        #input(result)
                                
                                summs_dict = dict()
                                tmp = copy.deepcopy(summarizers_list[i])
                                for j in range(len(tmp)):
                                    for k in range(len(key_list)):
                                        #summs = []
                                        for l in range(len(tmp[j][k])):
                                            #summs.append(summarizers[i][j][k])
                                            
                                            if key_list[k] in summs_dict.keys():
                                                summs_dict[key_list[k]].append(tmp[j][k][l])
                                            else:
                                                summs_dict[key_list[k]] = [tmp[j][k][l]]
                                                
                                summs_list = []
                                for key in key_list:
                                    summs_list.append(summs_dict[key])
                                
                                #print(summary_list[summary_index])
                                #input(res_)
                                for j in range(len(summs_list)):
                                    #print(summs_list)
            
                                    tmp = build_heatmap(heat_map_list[j],summary_list[i],summs_list[j],alpha_sizes[j]) 
                                    #print(summs_list[i/
                                    
                                    #print(res_[i])
                                    #print([[data_list[i][x],data_list[i][x+1]] for x in res_[i]])
                                    #input(res_)
                                    # IT data chart
                                    #if len(key_list) == 1:
                                    #for j in range(len(res_)):
                                        #print(res_[j],full_sax_rep[j])
                                    #print(res_[j])
                                    j_ = -1
                                    if len(key_list) > 1:
                                        j_ = j                                        
                                    show_provenance([key_list[j]],[data_list[j_]],tw,tmp,indices=res_[j],multicolor=True,trailing=True,single_day=single_summ[j],hours=(tw==0.04))      
                                    #print(tmp)
                                    #print(summs_list[j])
                                    #print(summarizers_list[i])
                                    #input(summary_list[i])   
                                #print()
                                #input()
                                break                            
                                  
                    print()
                        
                    if weekday_summaries != None:
                        for i in range(len(weekday_summaries)):
                            print(weekday_summaries[i])
                            print("Covering:",t3_list_[i]) 
                            print("Relevance:", coverage_list_[i])                   
                            print("Length quality:", length_list_[i])    
                            print("Simplicity:", simplicity_list_[i])
                            print()
                            
                            if provenance:
                                summarizers = summarizers_list_[i]
                                
                                #print(weekday_summaries[summary_index])
                                #print(summarizers)
                                prefixes = summarizers[0]
                                suffixes = summarizers[1]
                                
                                #print(prefixes,suffixes)
                                
                                first_letters = []
                                
                                #weekdays = []
                                pre_weekdays = []
                                for j in range(len(prefixes)):
                                    substr = ''
                                    for k in range(len(prefixes[j])):
                                        if prefixes[j][k] in date_column:
                                            if prefixes[j][k] not in pre_weekdays:
                                                pre_weekdays.append(prefixes[j][k])
                                        else:
                                            substr += summarizer_to_SAX(prefixes[j][k],alpha_sizes[j],attr=attr)
                                    first_letters.append(substr)
                                                      
                                second_letters = []
                                post_weekdays = []
                                for j in range(len(suffixes)):
                                    substr_ = ''
                                    for k in range(len(suffixes[j])):
                                        if suffixes[j][k] in date_column:
                                            if suffixes[j][k] not in post_weekdays:
                                                post_weekdays.append(suffixes[j][k])
                                        else:                            
                                            substr_ += summarizer_to_SAX(suffixes[j][k],alpha_sizes[j],attr=attr)
                                    second_letters.append(substr_)
                                                            
                                highlight_days = []
                                
                                weekday_mentions = set()
                                day_dict = dict()
                                for weekday in list(weekday_dict.values()):
                                    weekday_indices = set([j for j in range(len(weekday_summaries[i])) if weekday_summaries[i].startswith(weekday,j)])
                                    for item in weekday_indices:
                                        weekday_mentions.add(item) 
                                        day_dict[item] = weekday
                                weekday_mentions = sorted(list(weekday_mentions))
                                    
                                for j in range(len(key_list)):
                                    if attr != "Stock Market Data" and "Weather" not in attr:
                                        key_ = key_list[j].lower()
                                    else:
                                        key_ = key_list[j]
                                        if key_ == "Aapl Close Value" or key_ == "aapl close value":
                                            key_ = "AAPL close value"
                                        if key_ == "Aet Close Value" or key_ == "aet close value":
                                            key_ = "AET close value" 
                                        if key_ == "Alabama Temperature":
                                            key_ = "Alabama temperature"                                        
                                        if key_ == "Alaska Temperature":
                                            key_ = "Alaska temperature"                                            
                                    #print(weekday_summaries[i],key_)
                                    first_mention = [j for j in range(len(weekday_summaries[i])) if weekday_summaries[i].startswith(key_,j)][0]
                                    for j in range(len(weekday_mentions)):
                                        if first_mention < weekday_mentions[j]:
                                            highlight_days.append(day_dict[weekday_mentions[j]])
                                            break         
                                
                                
                                mention_indices = dict()
                                for j in range(len(key_list)):
                                    if attr != "Stock Market Data" and "Weather" not in attr:
                                        key_ = key_list[j].lower()
                                    else:
                                        if key_ == "Aapl Close Value" or key_ == "aapl close value":
                                            key_ = "AAPL close value"
                                        if key_ == "Aet Close Value" or key_ == "aet close value":
                                            key_ = "AET close value" 
                                        if key_ == "Alabama Temperature":
                                            key_ = "Alabama temperature"                                        
                                        if key_ == "Alaska Temperature":
                                            key_ = "Alaska temperature"
                                            
                                    attr_mentions = [j for j in range(len(weekday_summaries[i])) if weekday_summaries[i].startswith(key_,j)]
                                    #print(j,attr_mentions)
                                    for mention in attr_mentions:
                                        #print(mention_indices,mention)
                                        if mention in mention_indices.keys():
                                            mention_indices[mention].append(j)
                                        else:
                                            mention_indices[mention] = [j]
                                
                                #print(mention_indices)
                                mentions = sorted(list(mention_indices.keys()))
                                mention_index = 0
                                attr_days = [[] for j in range(len(key_list))]
                                #input(weekday_mentions)
                                for j in range(len(weekday_summaries[i])):
                                    if j != min(mentions) and j in mentions:
                                        mention_index += 1
                                        
                                    if j in weekday_mentions:
                                        #print(mentions[mention_index])
                                        #input(mention_indices)
                                        key_indices = mention_indices[mentions[mention_index]]
                                        for item in key_indices:
                                            attr_days[item].append(day_dict[j])
                                
                                letters_list = []
                                for j in range(len(first_letters)):
                                    letters_list.append(first_letters[j] + second_letters[j])  
                                
                                single_summ = [len(x) == 1 for x in letters_list]
                                #input(single_summ)
                                    
                                #print(pre_weekdays,post_weekdays)
                                #input(summarizers)
                                #print(prefixes)
                                max_length = max([len(x) for x in letters_list])
                                index = 0
                                for j in range(len(letters_list)):
                                    #print(prefixes[j])
                                    diff = max_length - len(letters_list[j])
                                    
                                    summ_ = False
                                    for k in range(len(prefixes[j])):
                                        if prefixes[j][k] in summarizer_7:
                                            #print(j,prefixes[j][k])
                                            summ_ = True
                                            
                                    if not summ_:
                                        letters_list[j] = '*'*diff + letters_list[j] 
                                    else:
                                        letters_list[j] = letters_list[j] + '*'*diff  
                                    
                                    #print(letters_list[j])
                                    
                                    if diff == 0:
                                        index = j                 
                                #print(weekdays)
                                #input(letters_list)
                                #input(index)
                                #input()
                                #for j in range(len(sax_list)):
                                    #print(sax_list[j])
                                #input()
                                if attr == "Heart Rate":
                                    res = [j for j in range(len(full_sax_rep)) if full_sax_rep.startswith(letters_list[index],j)]
                                else:
                                    res = [j for j in range(len(sax_list[index])) if sax_list[index].startswith(letters_list[index],j)]                                   
                                #res = [j for j in range(len(sax_list[index])) if sax_list[index].startswith(letters_list[index],j)]  
                                #input(res)
                                res = [j for j in res if j != len(date_column)-1 and date_column[j] in pre_weekdays and (date_column[j+1] in pre_weekdays or date_column[j+1] in post_weekdays)] # might need fixing
                                #print(date_column)
                                #print([j for j in range(len(date_column)) if date_column[j] in [pre_weekdays[1]]])
                                #input(res)
                                res_ = [[] for j in range(len(sax_list))]
                                for index in res:
                                    result = True
                                    info_ = []
                                    #input(letters_list)
                                    for j in range(len(sax_list)):
                                        candidate = ''
                                        length = 0
                                        #print(letters_list,i)
                                        while length < max_length and length < len(letters_list[j]):
                                            
                                            if letters_list[j][0] != '*' and letters_list[j][length] == '*':
                                                break
                                            #print(length)
                                            candidate += letters_list[j][length]
                                            length += 1
                                        
                                            
                                        #input([candidate,length,max_length])
                                        
                                        
                                        #result = result and (letters_list[i].strip('*') in sax_list[i][index:index+max_length])
                                        star_num = candidate.count('*')
                                        if attr == "Heart Rate":
                                            result = result and (candidate == full_sax_rep[index:index+length] or (candidate[0] == '*' and candidate[star_num:] == full_sax_rep[index+star_num:index+length]))
                                            info_.append([list(range(index,index+max_length)),letters_list[j],full_sax_rep[index:index+max_length]])   
                                        else:
                                            result = result and (candidate == sax_list[j][index:index+length] or (candidate[0] == '*' and candidate[star_num:] == sax_list[j][index+star_num:index+length]))
                                            info_.append([list(range(index,index+max_length)),letters_list[j],sax_list[j][index:index+max_length]])
                                        #print([result,candidate,sax_list[j][index:index+length],length])
                                        #input([letters_list[i],sax_list[i][index:index+max_length]])
                                    
                                    if result:
                                        
                                        #print(info_)
                                        for j in range(len(res_)):
                                            for k in range(len(info_[j][0])):
                                                #print([info_[j][1],info_[j][2],j,k])
                                                if info_[j][1][k] == info_[j][2][k] and info_[j][1][k] != '*' and info_[j][0][k] not in res_[j]:
                                                    #print(index,i)
                                                    #print(info_[i])
                                                    res_[j].append(info_[j][0][k])  
                                                    #print(j,res_[j])
                                                    #input()
                                                                        
                                # WIT data chart
                                summs_dict = dict()
                                for j in range(len(summarizers)):
                                    for k in range(len(key_list)):
                                        #summs = []
                                        for l in range(len(summarizers[j][k])):
                                            #summs.append(summarizers[i][j][k])
                                            
                                            if key_list[k] in summs_dict.keys():
                                                summs_dict[key_list[k]].append(summarizers[j][k][l])
                                            else:
                                                summs_dict[key_list[k]] = [summarizers[j][k][l]]
                                                
                                summs_list = []
                                for key in key_list:
                                    summs_list.append(summs_dict[key])
                                    
                                #print(pre_weekdays,post_weekdays)
                                #print(res_)
                                #print(date_column)
                                #input([j for j in range(len(date_column)) if date_column[j] in [pre_weekdays[0]]])                                                       
                                
                                for j in range(len(summs_list)):
            
                                    tmp = build_heatmap(heat_map_list[j],weekday_summaries[i],summs_list[j],alpha_sizes[j])  
                                    
                                    #if len(key_list) == 1:
                                    #show_provenance(key_list,data_list,tw,tmp,indices=res,multicolor=True,weekday_indices=[i for i in range(len(date_column)) if date_column[i] in pre_weekdays]) 
                                    #print(res_[j])
                                    #print(attr_days[j])
                                    #print([date_column[x] for x in res_[j]])
                                    res_[j] = [x for x in res_[j] if date_column[x] in attr_days[j]]
                                    
                                    #print(res_[j])
                                    
                                    #print([j for j in range(len(date_column)) if date_column[j] in [highlight_days[i]]]) 
                                    
                                    j_ = -1
                                    if len(key_list) > 1:
                                        j_ = j                                        
                                    show_provenance([key_list[j]],[data_list[j_]],tw,tmp,indices=res_[j],multicolor=True,weekday_indices=[k for k in range(len(date_column)) if date_column[k] in [highlight_days[j]]],trailing=True,single_day=single_summ[j],hours=(tw==0.04))                            
                                    #print()
                                #print() 
                                #input()
                                break                                                          
                             
                    # Multivariate general if-then pattern summaries
                    git_length = 30
                    sax_list_ = []
                    for i in range(len(sax_list)):
                        sax_list_.append(sax_list[i][-1*git_length:])                    
                    summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, summarizers_list = generateGIT(attr,key_list,sax_list_,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,arm_filepath=arm_filepath)
                    
                    if summaries != None:
                        for i in range(len(summaries)):
                            print("General if-then pattern summary:", summaries[i])
                            print("Truth value:", truth)
                            print("Imprecision:",t2_list[i])
                            print("Covering:",t3_list[i])                                            
                            print("Appropriateness:", t4_list[i])
                            print("Relevance:", coverage_list[i])
                            print("Length quality:", length_list[i])
                            print("Simplicity:", simplicity_list[i])
                            print() 
                            
                            if provenance:
                                #summarizers_list_ = summarizers_list[summary_index]
                                letters = []
                                #print(summarizers_list)
                                for i in range(len(summarizers_list[0])):
                                    summarizer = summarizers_list[0][i]
                                    #print(summarizer)
                                    
                                    letters.append(summarizer_to_SAX(summarizer,alpha_sizes[i],attr=attr))
                                
                                #data = sax_list[0]
                                #substr = first_letter + second_letter
                                #print(full_sax_rep)
                                #res = [i for i in range(len(full_sax_rep)) if full_sax_rep.startswith(substr,i)]
                                #for s in sax_list_:
                                    #print(s)
                                #input()
                                res = []
                                for i in range(len(sax_list_[0])):
                                    result = True
                                    for j in range(len(letters)):
                                        result = result and (letters[j] == sax_list_[j][i])
                                        
                                    if result:
                                        res.append(i)  
                                        
                                # GIT data chart
                                data_list_ = []
                                for i in range(len(data_list)):
                                    data_list_.append(data_list[i][-1*git_length:])   
                                    
                                for i in range(len(key_list)):
                                    tmp = build_heatmap(heat_map_list[i],summary,[summarizers_list[0][i]],alpha_sizes[i]) 
                                    i_ = -1
                                    if len(key_list) > 1:
                                        i_ = i                                                   
                                    show_provenance([key_list[i]],[data_list_[i_]],tw,tmp,indices=res,multicolor=True,single_day=True,hours=(tw==0.04))  
                                proto_cnt += 1  
                                break                            
                            
                            
                                
                    # Multivariate day-based pattern summaries       
                    summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, _ = generateDB(attr,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column,arm_filepath=arm_filepath)
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
                            
                            if provenance:
                                summs = []
                                words = summaries[i].split(' ')
                                
                                weekdays = list(weekday_dict.values())
                                day = None
                                for weekday in weekdays:
                                    if weekday in summaries[i]:
                                        day = weekday
                                        break                                
                                #print(summarizers,day_summary)
                                #print(words)
                                #print(summarizers)
                                for k in range(len(words)):
                                    word = words[k]
                                    if words[k-1] == "very" or words[k-1] == "within" or words[k-1] == "abnormally":
                                        word = words[k-1] + " " + word    
                                        
                                    
                                    #print(word)
                                    #print(word,summarizers_7)
                                    if word in summarizer_7:                                        
                                        summs.append(word)
                                
                                #summs = []
                                #for summarizer in summarizers:
                                    #if summarizer in day_summary:
                                        #for i in range(day_summary.count(summarizer)):
                                            #summs.append(summarizer)
                                        
                                #print(summs)
                                #print(day_summary)
                                #for i in range(len(sax_list)):
                                    #print(key_list[i],summs[i])
                                    #print([x for x in range(len(sax_list[i])) if sax_list[i][j] == summarizer_to_SAX(summs[i],alpha_sizes[i])])
                                #input()  
                                
                                dates = [i for i in range(len(date_column)) if date_column[i] == weekday]
                                
                                res = []
                                for j in range(len(dates)):
                                    #print()
                                    index_ = dates[j]
                                    result = True
                                    for i in range(len(sax_list)):
                                        #print(sax_list[i][index],summarizer_to_SAX(summs[i],alpha_sizes[i]),key_list[i])
                                        #print(i,index_)
                                        #print(sax_list)
                                        #print(summs)
                                        #print(alpha_sizes)
                                        #print(full_sax_rep,summs,alpha_sizes)
                                        if attr == "Heart Rate":
                                            result = result and (full_sax_rep[index_] == summarizer_to_SAX(summs[i],alpha_sizes[i],attr=attr))
                                        else:
                                            result = result and (sax_list[i][index_] == summarizer_to_SAX(summs[i],alpha_sizes[i],attr=attr))                                   
                                        #result = result and (sax_list[i][index_] == summarizer_to_SAX(summs[i],alpha_sizes[i],attr=attr))
                                    
                                    if result:
                                        res.append(index_)
                                        
                                #input(res)
                                # DB data chart
                                for j in range(len(key_list)):
                                    tmp = build_heatmap(heat_map_list[j],summaries[i],[summs[j]],alpha_sizes[j])    
                                    #print(tmp)
                                    #print(res)
                                    #if len(key_list) == 1:
                                    #print(res,len(data_list[i]))
                                    j_ = -1
                                    if len(key_list) > 1:
                                        j_ = j  
                                    #input(date_column)
                                    show_provenance([key_list[j]],[data_list[j_]],tw,tmp,indices=res,multicolor=True,weekday_indices=[k for k in range(len(date_column)) if date_column[k]==day],single_day=True,hours=(tw==0.04))
                                proto_cnt += 1 
                                break                            
                            
                                                                                
                                
                    # Goal assistance summary  
                    summary, length, simplicity = generateGA(attr,df_list,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column,arm_filepath=arm_filepath)
                    if summary != None:
                        print("Goal assistance summary:", summary)
                        print()
                        
                        if provenance:
                            for i in range(len(key_list)):
                                tmp = [{}]           
                                #if len(key_list) == 1:
                                i_ = -1
                                if len(key_list) > 1:
                                    i_ = i                                        
                                show_provenance([key_list[i]],[data_list[i_]],tw,tmp,showgoal=(key_list[i] == "Calorie Intake"),hours=(tw==0.04))                        
                        
                        proto_cnt += 1            
          
                                    
        print("Number of summaries produced:", proto_cnt)
        if proto_cnt > 0:
            user_cnt += 1
        all_cnt += proto_cnt
        print()
        proto_cnt = 0
                
print(all_cnt)
print(user_cnt)

        
