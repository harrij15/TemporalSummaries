#! python3
""" 
Citation for saxpy:
 Senin, P., Lin, J., Wang, X., Oates, T., Gandhi, S., Boedihardjo, A.P., Chen, C., Frankenstein, S., Lerner, M., GrammarViz 2.0: a tool for grammar-based pattern discovery in time series, ECML/PKDD Conference, 2014.
"""

import math
import os
import pandas as pd
from saxpy.sax import sax_via_window
import subprocess
import matplotlib.pyplot as plt
import datetime 
import numpy as np
import json
from saxpy.sax import ts_to_string
from saxpy.znorm import znorm
from saxpy.alphabet import cuts_for_asize
import random   
from squeezer import *

####### GENERAL SUMMARY FUNCTIONS #######

weekday_map = {"Monday" : 1,
                     "Tuesday" : 2,
                     "Wednesday" : 3,
                     "Thursday" : 4,
                     "Friday" : 5,
                     "Saturday" : 6,
                     "Sunday" : 7}  

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

def build_heatmap(heat_map,summary,summs,alpha_size): 
                            
    if summs == None:
        tmp = [{}]
        return tmp
                                
    tmp = []
    #print(summs)
    sub_dict = dict()
    for i in range(len(summs)):
        try:
            #print(summs[i])
            letter = summarizer_to_SAX(summs[i],alpha_size)
            sub_dict[letter] = heat_map[letter]
        except KeyError:
            pass
    tmp.append(sub_dict)
        
    #print(tmp)
        
    letters = list(heat_map.keys())
    for i in range(len(tmp)):
        sub_dict = tmp[i]
        for letter in letters:
            if letter not in sub_dict.keys():
                sub_dict[letter] = None
                
        tmp[i] = sub_dict    
        
    return tmp
            
def show_provenance(key_list,data_list,tw,heat_map_list,indices=None,multicolor=False,seq_length=1,region_index=None,weekday_indices=None,single_day=False,showgoal=False,pos=None,neg=None,comparison=False,summ_indices=None,trailing=False,hours=False):
    
    fig, ax = plt.subplots(figsize=(7.5,5))
    axes = [ax]
    key_str = ""      
    
    # Create heat maps
    left_map = heat_map_list[0]
    heat_colors = ['xkcd:aqua','xkcd:goldenrod','xkcd:green','xkcd:red','xkcd:violet']
    left_keys = list(sorted(left_map.keys()))
    for i in range(len(left_keys)):
        key = left_keys[i]
        if left_map[key] == None:
            continue
        #print(left_map[key]['min'],left_map[key]['max'])
        ax.bar(-1,left_map[key]['max']-left_map[key]['min'],bottom=left_map[key]['min'],width=(len(data_list[0])*2)+10,color=lighten_color(heat_colors[i],0.4))    
    
    heart_goal = False
    for i in range(len(key_list)):
        if i != 0:
            axes.append(ax.twinx())
        #ax = ax.twinx()
        #ax.set_xlabel("Days")
        #ax.set_ylabel("Calories Consumed")                    
        #ax.plot(data,label=key_list[i])
        key_str += key_list[i]
        if "Intake" not in key_list[i] and "close value" not in key_list[i] and "Average" not in key_list[i] and "Heart" not in key_list[i]:
            key_str += " Intake"
        if "close value" in key_list[i]:
            keys = key_str.split(" ")
            key_str = ""
            for j in range(len(keys)):
                if keys[j] != "and":
                    if keys[j] != "AET" and keys[j] != "AAPL":
                        key_str += keys[j].capitalize()
                    else:
                        key_str += keys[j]
                
                if j != len(keys)-1:
                    key_str += " "
                    
        if "Heart" in key_list[i]:
            heart_goal = True
                    
        if i != len(key_list)-1:
            key_str += " and "     
    
    plt.title(key_str + " Data",fontsize=20) 
    #plt.title(key_str + " Data") 
    #ax.legend(loc="upper right")
    #plt.grid()
    colors = ['xkcd:cerulean','xkcd:violet']
    locs = ["lower left", "lower right"]
    #input()
    if showgoal:
        if heart_goal:
            axes[0].plot([70]*(len(data_list[0])+1),color='Red')
            axes[0].plot([110]*(len(data_list[0])+1),color='Red')
        elif "Calorie Intake" in key_list:
            axes[0].plot([2000]*(len(data_list[0])+1),color='Red')
        
    for i in range(len(axes)):
        ax = axes[i]
        data = data_list[i]
        
        #if multicolor:
        first = True
        complete_color = False
        cnt = 0
        label_set = set()
        #input(indices)
        for j in range(len(data)):
            color = colors[i]
            label = None
            if multicolor and j in indices and not single_day and ((trailing and j+1 in indices) or not trailing):
                #print(j)
                color = 'xkcd:red orange'
            elif summ_indices != None:
                color = None
                for triple in summ_indices:
                    #print(j,pair[0])
                    if j >= triple[0] and j < triple[0]+tw:
                        color = heat_colors[triple[1]]
                        
                        label = triple[2]

                        if label not in label_set:
                            label_set.add(label)
                        else:
                            label = None
                        #print(label)
                        break
                
                if color == None:
                    color = colors[i]
                #print(j,region_index,posneg)
                #if j >= region_index and j < region_index+7:
                    #color = 'xkcd:goldenrod'    
                #elif j >= pos[i] and j < pos[i]+7:
                    #color = 'xkcd:apple green'
                #elif j >= neg[i] and j < neg[i]+7:
                    #color = 'xkcd:red orange'                
                #else:
                    #color = 'xkcd:cerulean'
                    
                #plt.axvspan(index,index+tw,color=color,alpha=0.5)                 
            else:
                #if single_day:
                    #color = 'xkcd:grey'                
                if first:
                    label = key_list[i]
                    first = False
                
            if j != len(data)-1:
                #print(j,j+1,data[j],data[j+1],color)
                #input(color)
                #ax.plot([j,j+1],[data[j],data[j+1]],color=color,label=label,linewidth=5,marker='o',markersize=10)
                ax.plot([j,j+1],[data[j],data[j+1]],color=color,label=label,linewidth=3)
            else:
                #print(j)
                if indices != None and j in indices and multicolor:
                    color = 'xkcd:red orange'
                #input(color)
                #ax.plot([j],[data[j]],color=color,label=label,linewidth=5,marker='o',markersize=10)
                ax.plot([j],[data[j]],color=color,label=label,linewidth=3)
            
            if complete_color == True:
                index = j
                if single_day or (j not in indices and j-1 in indices and trailing):
                    index = j-1
                #print(index,indices[len(indices)-1])
                if not (trailing and index not in indices):
                    #ax.plot([index],[data[index]],color='xkcd:red orange',label=None,linewidth=5,marker='o',markersize=10)
                    ax.plot([index],[data[index]],color='xkcd:red orange',label=None,linewidth=3,marker='o',markersize=5)
                #else:
                    #print(index,data[index])
                complete_color = False
            
            #print(j,indices)
            if multicolor and j in indices:
                complete_color = True
                
        #ax.plot(data,color=color,label=key_list[i],linewidth=2,marker='o')
        ax.legend(loc=locs[i],fontsize=14)
        
        label_str = key_list[i].split(" ")[0]
        if "close value" in key_list[i] or "Average" in key_list[i] or "Heart" in key_list[i]:
            label_str = key_list[i]
        else:
            if key_list[i].split(" ")[0] != "Protein" and key_list[i].split(" ")[0] != "Fat" and key_list[i].split(" ")[0] != "Sugar" and key_list[i].split(" ")[0] != "Sodium":
                label_str += "s" 
            label_str += " Consumed"
        ax.set_ylabel(label_str,fontsize=18)
        #ax.set_ylabel(label_str)
    
    if tw==0.04:
        axes[0].set_xlabel("Hours",fontsize=16)
    else:
        axes[0].set_xlabel("Weeks",fontsize=16)
    #axes[0].set_xlabel("Weeks")
    #axes[0].set_facecolor('xkcd:dark grey')
    axes_ = plt.gca()
    axes_.yaxis.grid()
    
    if indices != None and not multicolor:
        index_ = 0
        for index in indices:
            #if posneg != None:
                #if index == region_index:
                    #color = 'xkcd:goldenrod'        
                #elif index in posneg:
                    #color = 'xkcd:apple green'
                #else:
                    #color = 'xkcd:red orange'
                    
                #plt.axvspan(index,index+tw,color=color,alpha=0.5)
            #else:
            color = 'xkcd:goldenrod'
            #print(index,region_index)
            if index == region_index or (comparison and index_ > 0):
                color = 'xkcd:apple green'
                
            plt.axvspan(index,index+tw,color=color,alpha=0.5)
            
            index_ += 1
            
    if region_index != None: 
        axes[0].axvspan(region_index,region_index+tw,color='xkcd:goldenrod',alpha=0.5)
            
    #print(weekday_indices)
    if weekday_indices != None:
        for index in weekday_indices:
            #print(index)
            if single_day:
                #axes[0].axvline(index,color='xkcd:sage')
                axes[0].axvspan(index-0.3,index+0.3,color='xkcd:pale lime',alpha=0.5)  
            elif trailing:
                axes[0].axvspan(index-0.3,index+0.3,color='xkcd:pale lime',alpha=0.5) 
            elif index+1 < len(data): 
                axes[0].axvspan(index-0.3,index+1.3,color='xkcd:pale lime',alpha=0.5)        
    
    tw_ = tw
    multiple = 2
    if tw==0.04:
        tw_ = 1
        #input(len(data_list[0])))
        multiple = 1
    
    labels = [x+1 for x in range(0,math.ceil(len(data_list[0])/float(tw_)),multiple)]
    plt.xticks(np.arange(0, len(data), tw_*multiple),labels,fontsize=14)
    #labels = [x+1 for x in range(math.ceil(len(data_list[0])))]
    #plt.xticks(np.arange(0, len(data)),labels,fontsize=14)    
    plt.yticks(fontsize=14)    
    
    #for i in np.arange(0, len(data), tw):
        #axes[0].axvline(i,color='xkcd:sage')
        
    #input(left_map)
    if len(heat_map_list)>1:
        right_map = heat_map_list[1]
        for key in sorted(right_map.keys()):
            axes[1].bar(len(data_list[0]),right_map[key]['max']-right_map[key]['min'],bottom=right_map[key]['min'])    

    plt.xlim(-2,len(data_list[0])+0.5)
    
    bottom_min = min(data_list[0])
    if len(data_list) > 1:
        for i in range(1,len(data_list)):
            if min(data_list[i]) < bottom_min:
                bottom_min = min(data_list[i])
                
    axes[0].set_ylim(bottom=bottom_min-10) 
    if len(axes) > 1:
        axes[1].set_ylim(bottom=bottom_min-10)   
    
    #plt.rc('axes', titlesize=40)
    #fig.tight_layout()
    
    #plt.savefig("provenance/chart.jpg")
    plt.show()

def get_protoform(summarizer_type,attr_list,best_quantifier,summarizer_list,TW="weeks",x_val="days",qualifier_info=None,goals=None,ada_goal=None,tw_index=None):
    """
    Inputs:
    - summarizer_type: the type of summarizer
    - attr_list: the attribute list
    - best_quantifier: the quantifier chosen for the summarizer
    - summarizer_list: list of the conclusive phrases of a summary
    - TW: the time window size (default size is a week)
    - x_val: the x axis of the raw data
    - qualifier_info: information of qualifier
    
    Outputs the summary chosen
    
    Purpose: To gather the information required to fill in the protoforms and output
    the summaries
    """
    if TW != None:
        singular_TW = TW[:-1]
    else:
        singular_TW = None
        
    particle = "your"
    sub_particle = "your"
    #input(attr_list)
    weather_flag = False
    for i in range(len(attr_list)):
        attr = attr_list[i]
        if "temperature" in attr or attr == "Average Temperature" or "close value" in attr:
            weather_flag = True
    
    #print(weather_flag)
    if weather_flag:
        particle = "the"
        sub_particle = "its"
        
    #if "Stock Market Data" in attr_list:
        #stock_index = attr_list.index("Stock Market Data")
        #attr_list[index] = "close value"
    if "Past Daily TW" in summarizer_type:
        if qualifier_info != None:
            if len(qualifier_info[2]) == len(attr_list):
                return ""
            if "Generalized" in summarizer_type:
                summary = "In general, if"
                for i in range(len(qualifier_info[0])):
                    qual = qualifier_info[0][i]
                    if "close value" not in qual: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        qual = qual.lower()                    
                    summary += " " + particle + " " + qual  + " is " + qualifier_info[1][i]
                    if i != len(qualifier_info[0])-1:
                        summary += " and"                     
                
                summary += ", then"
                index = 0
                for i in range(len(attr_list)):
                    if i in qualifier_info[2]:
                        continue
                    
                    attribute_ = attr_list[i]
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()
                    
                    summary += " " + particle + " " + attribute_ + " is " + summarizer_list[index]
                    if index != len(summarizer_list)-1:
                        summary += " and"  
                    index += 1
                summary += "."
                return summary        
            elif "Food Items" in summarizer_type:
                qual = qualifier_info[0][0]
                index = attr_list.index(qual)
                summary = "On " + str(best_quantifier) + " days when you eat " + qual + ", you also eat " + attr_list[not index] + "."
                return summary
            else:
                #input(qualifier_info)
                if TW == "hours":
                    singular_TW = "day"
                    summary = "During " + str(best_quantifier) + " " + TW + " in the past " + singular_TW + ", when"
                elif goals != None:
                    summary = "On " + str(best_quantifier) + " " + x_val + ", when"
                else:
                    #print(best_quantifier,x_val,singular_TW)
                    summary = "On " + str(best_quantifier) + " " + x_val + " in the past " + singular_TW + ", when"
                for i in range(len(qualifier_info[0])):
                    attribute_ = qualifier_info[0][i]
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()             
                    if goals == None:
                        summary += " " + particle + " " + attribute_ + " was " + qualifier_info[1][i]
                    else:
                        summary += " you " + qualifier_info[1][i] + " " + particle + " " + attribute_ + " goal"
                    if i != len(qualifier_info[0])-1:
                        summary += " and"                     
                
                summary += ","
                index = 0
                for i in range(len(attr_list)):
                    if i in qualifier_info[2]:
                        continue
                    attribute_ = attr_list[i]
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower() 
                        
                    #input([index,summarizer_list])
                    if goals == None:
                        summary += " " + particle + " " + attribute_ + " was " + summarizer_list[index] 
                    else:
                        summary += " you " + summarizer_list[index] + " " + particle + " " + attribute_ + " goal"
                    if index != len(summarizer_list)-1:
                        summary += " and"  
                    index += 1
                summary += "."
                return summary
        elif "Breakfast" in attr_list:
            summary = "On " + str(best_quantifier) + " " + x_val
            if TW != None:
                summary += " in the past " + singular_TW 
            summary += ","
            
            summary += " you " + summarizer_list[0] + " a relatively fixed carbohydrate intake"
            
            summary += "."
            return summary
        else:
            if TW == "hours":
                summary = "During " + str(best_quantifier) + " " + TW
                singular_TW = "day"
            else:         
                summary = "On " + str(best_quantifier) + " " + x_val
                                
            if TW != None:
                summary += " in the past " + singular_TW 
            summary += ","
            #input(attr_list)
            for i in range(len(attr_list)):
                attribute_ = attr_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()
                
                tense = " has been "
                if TW == "hours":
                    tense = " was "
                    
                summary += " " + particle + " " + attribute_ + tense + str(summarizer_list[i])
                if i != len(attr_list)-1:
                    summary += " and"                        
            summary += "."
            return summary
    elif "Goal Evaluation" in summarizer_type:
        summary = "On " + str(best_quantifier) + " days"
        if "Cue" not in attr_list and TW != None and TW != -1:
            summary += " in the past " + singular_TW 
        summary += ","
        if "reach" in summarizer_list[0]:
            particle = "you"
        #print(ada_goal)
        if ada_goal != None and None not in goals and goals[0][0] != None and type(goals[0][0]) != int:
            if "fat percentage" in goals[0][0][0] and attr_list == ["Fat Intake"]:
                summary += " " + particle + " " + summarizer_list[0] + " " + sub_particle + " goal to obtain 20-35% of your calories from fat"
            elif "highcarblowfat" in goals[0][0][0] and "Fat Intake" in attr_list and "Carbohydrate Intake" in attr_list and len(attr_list) == 2:
                if "none" in best_quantifier:
                    summary = particle.capitalize() + " have not been conforming to a high-carb, low-fat diet"
                else:
                    summary += " " + particle + " maintained a high-carb, low-fat diet"
                    #if best_quantifier == "most of the" or best_quantifier == "all of the" or best_quantifier == "more than half of the":
                        #summary += "."
            elif "Energy Deficit" in attr_list:
                if "none" in best_quantifier:
                    summary = particle.capitalize() + " haven't always been achieving a 500-750 kcal/day energy deficit"
                else:
                    summary += " " + particle + " achieved a 500-750 kcal/day energy deficit"             
            elif "SatFatDecrease" in attr_list:
                if "none" in best_quantifier:
                    summary = particle.capitalize() + " haven't always been progressively decreasing your saturated fat intake"
                else:
                    summary += " " + particle + " progressively decreased your saturated fat intake"              
            elif "lowcarb" in goals[0][0]:
                if "none" in best_quantifier:
                    summary = particle.capitalize() + " haven't always been following a low-carbohydrate eating plan"
                else:
                    summary += " " + particle + " followed a low-carbohydrate eating plan"           
            elif "consistentcarb" in goals[0][0] and ada_goal == "culprit":
                meal = goals[0][0][1]
                #summary += " " + particle + " carbohydrate intake was " + summarizer_list[0] + " for " + meal.lower()  
                s = None
                #print(summarizer_list)
                if "low" in summarizer_list[0]:
                    s = "increasing"
                elif "high" in summarizer_list[0]:
                    s = "decreasing"
                
                if s == None:
                    summary = ""
                else:
                    summary = "To help maintain a relatively fixed carbohydrate intake, consider " + s + " your carbohydrate intake at " + meal.lower()
                
            elif "consistentcarb" in goals[0][0] and ada_goal == "meal":
                meal = goals[0][0][1]
                word = "during"
                if meal.lower() == "snacks":
                    word = "when eating"
                    
                if "none" in best_quantifier:
                    summary = particle.capitalize() + " haven't always been maintaining a relatively fixed level of carbohydrates " + word + " " + meal.lower()    
                else:
                    summary += " " + particle + " maintained a relatively fixed level of carbohydrates " + word + " " + meal.lower()                
                
            elif "consistentcarb" in goals[0][0]:
                #input(summary+" " + particle + " " + summarizer_list[0] + " " + sub_particle + " goal to keep a relatively fixed pattern of carbohydrates with respect to time and amount")
                if "none" in best_quantifier:
                    summary = "You haven't always been maintaining a relatively fixed level of carbohydrates throughout the day"
                else:
                    summary = "You've been maintaining a relatively fixed level of carbohydrates " + best_quantifier + " time throughout the day"
                #summary = "You haven't been 
                #summary += " " + particle + " " + summarizer_list[0] + " " + sub_particle + " goal to keep a relatively fixed pattern of carbohydrates with respect to time and amount"
            else:
                print(attr_list)
                print(goals[0][0])
                input("Need to add protoform")
        else:
            for i in range(len(attr_list)):
                prefix = "keep " + sub_particle + " "
                attribute_ = attr_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                
                suffix = attribute_
                if attr_list[i] == "Heart Rate":
                    goal = " within range"
                elif attr_list[i] == "Step Count" or attr_list[i] == "StepUp":
                    goal = " high"
                    if goals != None and None not in goals:
                        goal = " above " + sub_particle + " baseline"
                elif attr_list[i] == "Cue":
                    goal = ""
                    prefix = ""
                    suffix = ""
                    goals = goals[0]
                    if "10 minute" in goals:
                        goal = "take a 10-minute walk"
                        if "Cue" in summarizer_type:
                            goal += " around " + sub_particle + " habit time"
                    elif "destination" in goals:
                        goal = "to walk to " + sub_particle + " destination"
                else:
                    goal = " low"
                suffix += goal
                #input([attr_list,summarizer_list])
                summary += " " + particle + " " + str(summarizer_list[i]) + " " + sub_particle + " goal to " + prefix + suffix
                if i != len(attr_list)-1:
                    summary += " and"
        summary += "."
        return summary    
    elif "Trends" in summarizer_type:
        subtimeframe = " time,"
        if TW == "hours":
            subtimeframe = " day,"
            
        summary = str(best_quantifier) + subtimeframe
        if TW == "hours":
            summary = "During " + summary
        else:
            summary = summary.capitalize()
            
        for i in range(len(attr_list)):
            attribute_ = attr_list[i]
            if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                attribute_ = attribute_.lower()
                
            summary += " " + particle + " " + attribute_ + " " + str(summarizer_list[i])
            if i != len(attr_list)-1:
                summary += " and"
        
        timeframe = "day"
        if TW == "hours":
            timeframe = "hour"
        summary += " from one " + timeframe + " to the next."
        return summary
    elif "Pattern Recognition" in summarizer_type:
        summary = "During " + str(best_quantifier) + " " + TW + " similar to week " + str(tw_index+1) + ","
        for i in range(len(attr_list)):
            attribute_ = attr_list[i]
            if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                attribute_ = attribute_.lower()
                
            summary += " " + particle + " " + attribute_ + " " + str(summarizer_list[i])
            if i != len(attr_list)-1:
                summary += " and"    
        summary += " the next " + singular_TW + "."    
        return summary
    elif "Standard Pattern" in summarizer_type:
        if "Step Count":
            attr = "step count"
        
        part_ = "you had"
        subpart_ = "your"
        
        temp_flag = False
        index_list = []
        if type(attr_list) is list:
            for j in range(len(attr_list)):
                if "temperature" in attr_list[j] or attr_list[j] == "Average Temperature":
                    temp_flag = True
        else:
            if "temperature" in attr_list or "Average Temperature" in attr_list:
                temp_flag = True
                
        if temp_flag:
            part_ = "there was"
            subpart_ = "the"
        summary = "The last time " + part_ + " a " + singular_TW + " similar to week " + str(tw_index+1) + ","
        for i in range(len(attr_list)):
            attribute_ = attr_list[i]
            if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                attribute_ = attribute_.lower()            
            summary += " " + subpart_ + " " + attribute_ + " " + str(summarizer_list[i])
            if i != len(attr_list)-1:
                summary += " and"    
        summary += " the next " + singular_TW + "."   
        return summary
    elif "Day-based pattern summary" in summarizer_type:
        summary = ""
        if "Breakfast" not in attr_list:
            for i in range(len(attr_list)):
                if goals != None:
                    first = "You "
                    if i != 0:
                        first =  " " + first.lower()
                    summary += first
                elif i == 0:
                    summary += particle.capitalize() + " "           
                else:
                    summary += " " + particle + " "
                    
                #if attr_list[i] == "Step Count":
                    #attr_list[i] = "step count"
                    #if summarizer_list[i] == "did not reach":
                        #summarizer_list = "not reach"
                    #else:
                        #summarizer_list = "reach"                    
                    #summary += attr_list[i].lower() + " tends to " + str(summarizer_list[i]) + " your " + attr_list[i].lower() + " goal"
                #else:
                attribute_ = attr_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()    
                    
                #input(summary)
                if goals != None:
                    summary += "tend to " + summarizer_list[i] + " " + particle.lower() + " " + attribute_ + " goal"
                else:
                    summary += attribute_ + " tends to be " + str(summarizer_list[i])
                    
                if i != len(attr_list)-1:
                    summary += " and"    
        else:
            summarizer = "relatively fixed"
            word = ""
            if summarizer_list[0] == "did not have":
                #summarizer = "inconsistent"
                word = "not "
            
            summary += particle.capitalize() + " carbohydrate intake tends to " + word + "be " + summarizer
                
        #if goals != None:
            #summary += " on " + best_quantifier + " " + x_val + "s."
        #else:
        summary += " on " + x_val + "s."
            
        return summary
    elif "Goal Assistance" in summarizer_type:
        summary = "In order to better follow the " + qualifier_info[0] + ", you should"
        for i in range(len(summarizer_list)):
            attr = attr_list[i]
            if attr[-1] == "s":
                attr = attr[:-1]
                
            attribute_ = attr
            if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                attribute_ = attribute_.lower()            
                
            summary += " " + summarizer_list[i] + " " + particle + " " + attribute_ 
            if attr != "Calorie Intake":
                summary += " intake"
            if len(summarizer_list) == 1:
                break
            
            if i != len(summarizer_list)-1:
                if len(summarizer_list) != 2:
                    summary += ","
                
                if i == len(summarizer_list)-2:
                    summary += " and"
                
        summary += "."
        return summary
    elif "Arm Comparison" in summarizer_type:
        summary = None
        arm = qualifier_info[0]
        past_summarizer = qualifier_info[1]
        proto_type = qualifier_info[2]
        attribute = qualifier_info[3]
        qualifier = qualifier_info[4]
        time_window = qualifier_info[5]
        
        group = "this study"
        if arm != None and len(arm) > 0:
            group = arm
        
        if "10-minute" in proto_type:
            summary = best_quantifier.capitalize() + " participants in the " + arm + " study arm " + past_summarizer
            blurb = " their goal to have a 10-minute walk"
            summary += blurb + " " + summarizer_list[0] + " time."
        elif proto_type == "SETW":
            summary = best_quantifier.capitalize() + " participants in " + group + " had " 
            if ',' in summarizer_list[0]:
                summ_list = summarizer_list[0].split(',')
                attribute_list = attribute.split(',')
                #print(attribute_list).
                    
                    
                for i in range(len(summ_list)):
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                    
                    summary += "a " + summ_list[i].strip() + " " + attribute_
                    if len(summ_list) == 1:
                        break
                    
                    if i != len(summ_list)-1:
                        if len(summ_list) != 2:
                            summary += ","
                        
                        if i == len(summ_list)-2:
                            summary += " and "
            else:
                summary += "a " + summarizer_list[0] + " " + attribute.lower()
                
            if time_window == 7:
                blurb = " in the past full week"
            elif time_window == 30:
                blurb = " in the past full month"                
            elif time_window == -1:
                blurb = ""
            summary += blurb + '.'
        elif proto_type == "SEsTW":
            summary = best_quantifier.capitalize() + " participants in " + group + " had " 
            attribute_list = attribute.split(',')
            
            #print("here",summarizer_list)
            #if type(summarizer_list[0]) != list:
                #summarizer_list
            #summarizer_list = [summarizer_list]
            #print("start")
            for i in range(len(summarizer_list)):
                #print("l",summarizer_list[i])
                #try:
                summarizers = summarizer_list[i][0]
                quantifier = summarizer_list[i][1]
                #except IndexError:
                    #summarizers = summarizer_list
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()             
                            
                        summary += "a " + summarizers[j].strip() + " " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    #print(attribute_list)
                    attribute_ = attribute_list[0].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += "a " + summarizers + " " + attribute_
                    
            summary += " on " + quantifier 
            if time_window == 7:
                blurb = " days in the past week"
            elif time_window == 30:
                blurb = " days in the past month"              
            elif time_window == -1:
                blurb = " days"
            #print(time_window)
            summary += blurb + '.'            
            #input(summary)
        elif proto_type == "SEsTWQ":
            #input([attribute,qualifier])
            summary = best_quantifier.capitalize() + " participants in " + group + " had " 
            summ_map = dict()
            attribute_list = attribute.split(',')      
            summarizers = summarizer_list[0][0]
            summarizers = summarizers.split(',')
            quantifier = summarizer_list[0][1]
            attribute_list = attribute_list[0].split('|')
            print(attribute)
            for i in range(len(attribute_list)):
                
                attribute_list[i] = attribute_list[i].strip()
                #print(summarizer_list)
                
                
                #input([summarizers,attribute_list])
                #print(attribute_list[i])
                summ_map[attribute_list[i].strip()] = summarizers[i].strip()
            qualifier_list = qualifier.split(',')
            
            
            attribute_list = list(set(attribute_list) - set(qualifier_list))
            #print(attribute_list,qualifier_list)
            #input(summ_map)
            #print(summarizer_list)
            #input([attribute_list,qualifier_list])
            print(attribute_list)
            for j in range(len(attribute_list)):
                attribute_ = attribute_list[j].strip()
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                summary += "a " + summ_map[attribute_list[j].strip()].strip() + " " + attribute_
                if len(attribute_list) == 1:
                    break
                
                if j != len(attribute_list)-1:
                    if len(attribute_list) != 2:
                        summary += ","
                    
                    if j == len(attribute_list)-2:
                        summary += " and "                  
            
            summary += ", when they had "
            for j in range(len(qualifier_list)):
                #print(summ_map)
                summary += "a " + summ_map[qualifier_list[j].strip()].strip() + " " + qualifier_list[j].strip().lower()
                if len(qualifier_list) == 1:
                    break
                
                if j != len(qualifier_list)-1:
                    if len(qualifier_list) != 2:
                        summary += ","
                    
                    if j == len(qualifier_list)-2:
                        summary += " and "                    
                    
            summary += " on " + quantifier  
            if time_window == 7:
                blurb = " days in the past week"
            elif time_window == 30:
                blurb = " days in the past month"              
            elif time_window == -1:
                blurb = " days"
            summary += blurb + '.'             
        elif proto_type == "EC":
            summary = best_quantifier.capitalize() + " participants in " + group + " had " 
            attribute_list = attribute.split(',')     
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                indices = summarizer_list[i][1].split(',')
                first_index = indices[0]
                second_index = indices[1]                
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        if "about the same" in summarizers[j]:
                            summarizers[j] = "similar"
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += "a " + summarizers[j].strip() + " " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and " 
                        else:
                            if time_window == 7:
                                pre_blurb = " in week "
                            elif time_window == 30:
                                pre_blurb = "in month " 
                            summary += pre_blurb + str(first_index)                        
                else:
                    if "about the same" in summarizers:
                        summarizers = "similar"                   
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += "a " + summarizers + " " + attribute_           
            #print(best_quantifier,attribute,summarizer_list)
            pre_blurb = " than"
            if summarizers == "about the same" or summarizers == "similar":
                pre_blurb = " to what"
                            
            if time_window == 7:
                #blurb = pre_blurb + " they did the week before"
                blurb = pre_blurb + " they did in week " + str(second_index)
            elif time_window == 30:
                #blurb = pre_blurb + " they did the month before"   
                blurb = pre_blurb + " they did in month " + str(second_index)              
            summary += blurb + '.'             
            #input(summary)    
        elif proto_type == "GC":
            summary = best_quantifier.capitalize() + " participants in " + group + " did " 
            attribute_list = attribute.split(',') 
            qualifier_list = qualifier.split(',')
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                indices = summarizer_list[i][1].split(',')
                first_index = indices[0]
                second_index = indices[1]
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += summarizers[j].strip() + " with keeping their " + attribute_ + " " + qualifier_list[j].strip()
                        
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "  
                        else:
                            if time_window == 7:
                                pre_blurb = " in week "
                            elif time_window == 30:
                                pre_blurb = "in month " 
                            summary += pre_blurb + str(first_index)
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += summarizers + " with keeping their " + attribute_ + " " + qualifier.strip() 
            #print(best_quantifier,attribute,summarizer_list)
            
            pre_blurb = " as"
            if summarizers == "better":
                pre_blurb = " than"
            
            if time_window == 7:
                #blurb = pre_blurb + " they did the week before"
                blurb = pre_blurb + " they did in week " + str(second_index)
            elif time_window == 30:
                #blurb = pre_blurb + " they did the month before"   
                blurb = pre_blurb + " they did in month " + str(second_index)
                
            summary += blurb + '.' 
        elif proto_type == "GE":
            summary = best_quantifier.capitalize() + " participants in " + group + " " 
            attribute_list = attribute.split(',')
            qualifier_list = qualifier.split(',')
            
            #print("here",summarizer_list)
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                quantifier = summarizer_list[i][1]
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += summarizers[j].strip() + " their goal to keep their " + attribute_ + " " + qualifier_list[j].strip()
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += summarizers + " their goal to keep their " + attribute_ + " " + qualifier.strip()
                    
            summary += " on " + quantifier  
            if time_window == 7:
                blurb = " days in the past week"
            elif time_window == 30:
                blurb = " days in the past month"              
            elif time_window == -1:
                blurb = " days"
            summary += blurb + '.'             
        elif proto_type == "ST":
            summary = best_quantifier.capitalize() + " participants in " + group + " " 
            attribute_list = attribute.split(',')
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                quantifier = summarizer_list[i][1]
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[i].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += summarizers[j].strip()[:-1] + " their " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += summarizers[:-1] + " their " + attribute_          
            summary += " from one day to the next " + quantifier + " time."
        elif proto_type == "CB":
            if time_window == 7:
                blurb = "weeks"
            elif time_window == 30:
                blurb = "months"              
                
            summary = "After looking at clusters containing " + blurb + " similar to this past one, it can be seen that " + best_quantifier + " participants with these clusters may see " 
            
            attribute_list = attribute.split(',')
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                
                summarizer_map = {"rose" : "a rise",
                                  "stayed the same" : "little to no change",
                                  "dropped" : "a drop"}
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += summarizer_map[summarizers[j].strip()] + " in their " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += summarizer_map[summarizers] + " in their " + attribute_
                
            if time_window == 7:
                blurb = " next week"
            elif time_window == 30:
                blurb = " next month"                 
            summary += blurb + "."
        elif proto_type == "SP":
            if time_window == 7:
                blurb = "weeks"
            elif time_window == 30:
                blurb = "months"              
                
            summary = "Based on the most recent " + blurb + " similar to this past one, it can be seen that " + best_quantifier + " participants may see " 
            
            attribute_list = attribute.split(',')
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                
                summarizer_map = {"rose" : "a rise",
                                  "stayed the same" : "little to no change",
                                  "dropped" : "a drop"}
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += summarizer_map[summarizers[j].strip()] + " in their " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += summarizer_map[summarizers] + " in their " + attribute_ 
                
            if time_window == 7:
                blurb = " next week"
            elif time_window == 30:
                blurb = " next month"                 
            summary += blurb + "."            
        elif proto_type == "IT":
            summary = "For " + best_quantifier + " participants in " + group + ", it is true that when" 
            attribute_list = attribute.split('|')[0].split(',')
            second = ""
            third = ""
            abort = False
            weekday_index = 0
            num_summarizers = 0
            summarizers1 = []
            summarizers2 = []
            weekdays = None
          
            #print(summarizer_list)
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                items = summarizers.split(';')
                items1 = items[0].split(',')
                items2 = items[1].split(',')
                
                items1 = [x for x in items1 if len(x)>0]
                items2 = [x for x in items2 if len(x)>0]
                #print(items1,items2)
                
                sublist = []
                for j in range(len(items1)):
                    #print(items1[j])
                    if '_' in items1[j]:
                        s = items1[j].split('_')
                        sublist.append(s[0])
                        summarizers1.append(sublist)
                        sublist = [s[1]]
                    else:
                        sublist.append(items1[j])
                        
                summarizers1.append(sublist)
                
                sublist = []      
                for j in range(len(items2)):
                    if '_' in items2[j]:
                        s = items2[j].split('_')
                        sublist.append(s[0])
                        summarizers2.append(sublist)
                        sublist = [s[1]]
                    else:
                        #print(items2[j],sublist,j)
                        sublist.append(items2[j])    
                        
                #print(sublist,len(items2))
                summarizers2.append(sublist)
                 
            #print(summarizers1)
            #print(summarizers2)
            for i in range(len(summarizers1)):
                if len(summarizers1[i]) == 0 or summarizers1[i][0] == '' or i>=len(attribute_list):
                    continue
                if second != "":
                    second += ", and"
                attribute_ = attribute_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                second += " their " + attribute_.strip() + " follows the pattern of being "
                for j in range(len(summarizers1[i])):
                    if third != "":
                        third += ", then "
                    third += summarizers1[i][j] 
                    
                    #if weekdays != None:
                        #third += " on a " + weekday_dict[int(weekday_list[p][weekday_index])]
                        #result_summarizers[p][0][i].append(weekday_dict[int(weekday_list[p][weekday_index])])
                        #weekday_index += 1
                    #num_summarizers += 1
                second += third
                third = ""
            
            fourth = ","
            fifth = ""
          
            #input(summarizers2)
            for i in range(len(summarizers2)):
                if len(summarizers2[i]) == 0 or summarizers2[i][0] == '' or i>=len(attribute_list):
                    continue 
                
                #print(summarizers2[i],len(summarizers2[i]))
                    
                if fourth != "," and i == len(summarizers2)-1:
                    fourth += " and"            
                attribute_ = attribute_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                fourth += " their " + attribute_.strip() + " tends to be "
                for j in range(len(summarizers2[i])):
                    if fifth != "":
                        fifth += ", then "                
                    fifth += summarizers2[i][j]
                    #if weekdays != None:
                        #fifth += " the next " + weekday_dict[int(weekday_list[p][weekday_index])]
                        
                    num_summarizers += 1
                fourth += fifth
                fifth = ""            
    
            if weekdays == None:
                sixth = " the next day."
            else:
                sixth = '.'
                    
            summary += second + third + fourth + fifth + sixth 
            #input(summary)
        elif proto_type == "WIT":
            summary = "For " + best_quantifier + " participants in " + group + ", it is true that when"
            attribute_list = attribute.split('|')[0].split(',')
            second = ""
            third = ""
            abort = False
            num_summarizers = 0
            summarizers1 = []
            summarizers2 = []
            weekdays = []
            weekday_index = 0
            
            #input(attribute_list)
            #weekdays = None
          
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                items = summarizers.split(';')
                #print(summarizers)
                #print(items)
                
                
                it = items[0].split('_')
                #print(it)
                for it_ in it:
                    if len(it_) == 0 and len(summarizers1) < 2:
                        summarizers1.append('')
                        continue
                    part = it_.split(',')
                    index = int(len(part)/2)
                    sublist = []
                    
                    for summ in part[:index]:
                        sublist.append(summ)
                    if len(sublist)>0:
                        summarizers1.append(sublist)                    
                    
                    for wd in part[index:]:
                        if wd != '':
                            weekdays.append(wd)  
                    
                    #part = it_.split(',')
                    #summarizers1.append([part[0]])
                    #weekdays.append(part[1])
                
                #print(summarizers1,weekdays)
                
                it = items[1].split('_')
                #print(it)
                for it_ in it:
                    if len(it_) == 0 and len(summarizers2) < 2: 
                        summarizers2.append('')
                        continue
                    part = it_.split(',')
                    index = int(len(part)/2)
                    sublist = []
                    
                    for summ in part[:index]:
                        sublist.append(summ)
                    if len(sublist)>0:
                        summarizers2.append(sublist)
                    
                    for wd in part[index:]:
                        if wd != '':
                            weekdays.append(wd)
                            
                #print(summarizers2,weekdays)
                #input()
                #input(it)
                #summarizers1.append([it[0]])
                #weekdays.append(it[1])
                
                #it = items[1].split('_')
                #for it_ in it:
                    #if len(it_) == 0:
                        #summarizers2.append('')
                        #continue
                    
                    #part = it_.split(',')
                    #summarizers2.append([part[0]])
                    #weekdays.append(part[1])
                #summarizers1.append([it[0]])
                #weekdays.append(it[1])                
                
                #s1 = items[0].strip('_').split(',')
                #s2 = items[1].strip('_').split(',')
                #print(s1)
                #print(s2)
                #index1 = int(len(s1)/2.0)
                #index2 = int(len(s1)/2.0)
                #for s in s1[index1:]:
                    #weekdays.append(s)
                #for s in s2[index2:]:
                    #weekdays.append(s)
                
                #summarizers1.append([s1[0]])
                #summarizers2.append([s2[0]])
                #input(items).
                #for j in range(len(items)):
                    #items[j] = items[j].split('_')
                    
            #input([summarizers1,summarizers2])   
            #print(summarizers1,summarizers2)
            #print(weekdays)
            for i in range(len(summarizers1)):
                if len(summarizers1[i]) == 0 or summarizers1[i][0] == '' or i>=len(attribute_list):
                    continue
                if second != "":
                    second += ", and"
                attribute_ = attribute_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                second += " their " + attribute_.strip() + " follows the pattern of being "
                #print(summarizers1[i])
                for j in range(len(summarizers1[i])):
                    if third != "":
                        third += ", then "
                    third += summarizers1[i][j] 
                    
                    if weekdays != None:
                        third += " on a " + weekdays[weekday_index]
                        #result_summarizers[p][0][i].append(weekday_dict[int(weekday_list[p][weekday_index])])
                        weekday_index += 1
                    #num_summarizers += 1
                second += third
                third = ""
            
            fourth = ","
            fifth = ""
          
            for i in range(len(summarizers2)):
                if len(summarizers2[i]) == 0 or summarizers2[i][0] == '' or i>=len(attribute_list):
                    continue            
                    
                if fourth != "," and i == len(summarizers2)-1:
                    fourth += " and"         
                attribute_ = attribute_list[i]
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                fourth += " their " + attribute_.strip() + " tends to be "
                for j in range(len(summarizers2[i])):
                    if fifth != "":
                        fifth += ", then "                
                    fifth += summarizers2[i][j]
                    if weekdays != None:
                        fifth += " on a " + weekdays[weekday_index]
                        weekday_index += 1
                    num_summarizers += 1
                fourth += fifth
                fifth = ""            
    
            if weekdays == None:
                sixth = " the next day."
            else:
                sixth = '.'
                    
            summary += second + third + fourth + fifth + sixth            
            #input(summary)
            #input(best_quantifier)
        elif proto_type == "GIT":
            #print(best_quantifier,attribute,qualifier,summarizer_list)
            summary = "For " + best_quantifier + " participants in " + group + ", it is true that when they had "
            attribute_list = attribute.split('|')[0].split(',')
            summ_map = dict()
            attribute_list = attribute.split(',')      
            summarizers = summarizer_list[0][0]
            summarizers = summarizers.split(',')
            quantifier = summarizer_list[0][1]
            attribute_list = attribute_list[0].split('|')
            for i in range(len(attribute_list)):
                
                attribute_list[i] = attribute_list[i].strip()
                #print(summarizer_list)
                
                
                #input([summarizers,attribute_list])
                #print(attribute_list[i])
                summ_map[attribute_list[i].strip()] = summarizers[i].strip()
            qualifier_list = qualifier.split(',')
            
            
            attribute_list = list(set(attribute_list) - set(qualifier_list))
            #print(attribute_list,qualifier_list)
            for j in range(len(qualifier_list)):
                summary += "a " + summ_map[qualifier_list[j].strip()].strip() + " " + qualifier_list[j].strip().lower()
                if len(qualifier_list) == 1:
                    break
                
                if j != len(qualifier_list)-1:
                    if len(qualifier_list) != 2:
                        summary += ","
                    
                    if j == len(qualifier_list)-2:
                        summary += " and "    
            summary += ", they had "
            
            for j in range(len(attribute_list)):
                attribute_ = attribute_list[j].strip()
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                summary += "a " + summ_map[attribute_list[j].strip()].strip() + " " + attribute_
                if len(attribute_list) == 1:
                    break
                
                if j != len(attribute_list)-1:
                    if len(attribute_list) != 2:
                        summary += ","
                    
                    if j == len(attribute_list)-2:
                        summary += " and "            
            summary += "."
            #input(summary)
        elif proto_type == "DB":
            summary = best_quantifier.capitalize() + " participants in " + group + " tend to have " 
            attribute_list = attribute.split('|')[0].split(',')
            
            #print("here",summarizer_list)
            for i in range(len(summarizer_list)):
                summarizers = summarizer_list[i][0]
                quantifier = summarizer_list[i][1]
                
                if ',' in summarizers:
                    summarizers = summarizers.split(',')
                    for j in range(len(summarizers)):
                        attribute_ = attribute_list[j].strip()
                        if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                            attribute_ = attribute_.lower()                            
                        summary += "a " + summarizers[j].strip() + " " + attribute_
                        if len(summarizers) == 1:
                            break
                        
                        if j != len(summarizers)-1:
                            if len(summarizers) != 2:
                                summary += ","
                            
                            if j == len(summarizers)-2:
                                summary += " and "   
                else:
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += "a " + summarizers + " " + attribute_
                    
            summary += " on " + qualifier + "s." 
        elif proto_type == "GA":
            summary = best_quantifier.capitalize() + " participants in " + group + " have been given advice " 
            attribute_list = attribute.split(',')
            if ',' in summarizer_list[0][0]:
                summ_list = summarizer_list[0][0].split(',')
                
                #print(attribute_list,summ_list)
                for i in range(len(summ_list)):
                    attribute_ = attribute_list[i].strip()
                    if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                        attribute_ = attribute_.lower()                        
                    summary += "to " + summ_list[i].strip() + " their " + attribute_
                    if len(summ_list) == 1:
                        break
                    
                    if i != len(summ_list)-1:
                        if len(summ_list) != 2:
                            summary += ","
                        
                        if i == len(summ_list)-2:
                            summary += " and "
            else:
                attribute_ = attribute_list[0].strip()
                if "close value" not in attribute_: #and "temperature" not in attribute_ and attribute_ != "Average Temperature":
                    attribute_ = attribute_.lower()                    
                summary += "to " + summarizer_list[0][0] + " their " + attribute_
                
            summary +=  '.'            
        if summary == None:
            input(proto_type)
        return summary
    
    elif "Food Preferences" in summarizer_type:
        index = summarizer_type.find("-")
        food = summarizer_type[index+2:]
        summary = best_quantifier.capitalize() + " time, you " + summarizer_list[0] + " " + food
        return summary
                
    return ""

def generateSETW(attr,key_list,pid_list,singular_TW,past_full_wks,tw_sax_list,letter_map_list,alpha_sizes,tw,tw_sax,age=None,activity_level=None,arm_filepath=None,quick=False):
    
    if quick:
        summaries, _ = get_single_SAX_summary(key_list,tw_sax,letter_map_list,alpha_sizes,singular_TW,tw_size=tw,past_tw=past_full_wks,age=age,activity_level=activity_level)
        return summaries
    
    if "close value" in key_list: 
        for i in range(len(key_list)):
            key_list[i] = pid_list[i] + " " + key_list[i]
    if "Activity" not in key_list and tw > 0.04 and attr != "MyFitnessPalMeals":
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
            
            tw_summary, tw_summarizers = get_single_SAX_summary(key_list,
                                                                past_tw_letters,
                                                                letter_map_list,
                                                                alpha_sizes,
                                                                singular_TW,
                                                                tw_size=tw,
                                                                past_tw=past_full_wks,
                                                                age=age,
                                                                activity_level=activity_level)
        
        if tw_summary != None:
            length = get_summary_length(len(tw_summarizers))
            simplicity = get_simplicity(len(tw_summarizers)+1)
            
            query_ = [["current index",[0]]] 
            tmp = []
            for item in tw_sax_list:
                tmp.append(item[-1])  
                
            t3, coverage = degree_of_covering(key_list,tmp,tw_summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
            t4 = degree_of_appropriateness(key_list,tmp,tw_summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)
            
            if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
            
            return [tw_summary,t3,coverage,t4,length,simplicity,first, tw_summarizers]
    if quick:
        return [None]*2    
    return [None]*8

def generateSESTW(attr,key_list,sax_list,letter_map_list,alpha,alpha_sizes,TW,quick=False,start_day=None,end_day=None,age=None,activity_level=None,arm_filepath=None,food_items=False):
    summarizer_type = "Past Daily TW - "
    if not food_items:
        for i in range(len(key_list)):
            summarizer_type += key_list[i]
        
            if i != len(key_list)-1:
                summarizer_type += " and " 
    else:
        summarizer_type += "Food Items"
            
    summarizer_7 = ["extremely low","very low","low","moderate","high","very high","extremely high"]
    
    summarizer_list = []
    for i in range(len(key_list)):
        summarizers = ["very low","low","moderate","high","very high"]
        
        if alpha_sizes[i] == 7:
            summarizers = summarizer_7                    
        summarizer_list.append(summarizers)
                
    avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizer_list,
                                                                                           summarizer_type,
                                                                                           key_list,
                                                                                           sax_list,
                                                                                           letter_map_list,
                                                                                           alpha_sizes,
                                                                                           alpha,
                                                                                           xval="days",
                                                                                           TW=TW)
    
    if quantifier_list == None:
        return [None]*8
    
    index = best_quantifier_index(quantifier_list,t1_list)
    if quick:
        return [[summary_list[index]],[t1_list[index]]]
    
    daily_summary = summary_list[index]
    summarizer_list = summarizer_list[index]
    truth = t1_list[index]
    average = avg_list[index]
    if daily_summary != None:
        length = get_summary_length(len(summarizer_list))
        simplicity = get_simplicity(len(summarizer_list)+1)
        query_ = [["through",0,7]]
        tmp = []
        for item in sax_list:
            #print(start_day,end_day)
            tmp.append(item[start_day:end_day])  
            #print(len(item))
        #input([start_day,end_day])
        t2 = degree_of_imprecision(avg_list)
        t3, coverage = degree_of_covering(key_list,tmp,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
        t4 = degree_of_appropriateness(key_list,tmp,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level) 
        
        if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
        
        return [daily_summary, truth, t2, t3, coverage, t4, length, simplicity, summarizer_list]
    
    if quick:
        return [None]*2    
    return [None]*8   

def generateSESTWQ(attr,key_list,past_tw_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,TW,age,activity_level,day_sax=None,arm_filepath=None,food_items=False,quick=False,goals=None,summarizer_type=None,constraint=False):
    
    if summarizer_type is None:
        summarizer_type = "Past Daily TW w/ Qualifier- " 
        
    if not food_items:
        for i in range(len(key_list)):
            summarizer_type += key_list[i]
        
            if i != len(key_list)-1:
                summarizer_type += " and " 
    else:
        summarizer_type += "Food Items"
    
    summarizers = ["very low","low","moderate","high","very high"]
    if food_items:
        summarizers = ["eaten","not eaten"]
    if goals != None:
        summarizers = ["reached","did not reach"]
            
    summarizer_list = []
    for i in range(len(key_list)):
        if alpha_sizes[i] == 7:
            summarizers = summarizer_7        
        summarizer_list.append(summarizers)   
        
    if attr == "MyFitnessPalMeals":
        summarizer_list = [summarizer_list[0]]
        
    from itertools import combinations
    key_combos = []
    for i in range(len(key_list)):
        key_comb = combinations(key_list,i+1)
        key_combos.append(list(key_comb))  
    
    summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, summarizers_lists = [], [], [], [], [], [], [], [], []
    
    # TODO: get rid of repeats
    for key_combo in key_combos:
        for flag_ in key_combo:
            flag_ = list(flag_)
            if len(flag_) == len(key_list) or attr == "MyFitnessPalMeals":
                continue
            
            avg_list, t1_list, quantifier_list, summary_list, summarizers_list = generate_summaries(summarizer_list,
                                                                                                    summarizer_type,
                                                                                                    key_list,
                                                                                                    past_tw_list,
                                                                                                    letter_map_list,
                                                                                                    alpha_sizes,
                                                                                                    alpha,
                                                                                                    TW=TW,
                                                                                                    xval="days",
                                                                                                    flag=flag_,
                                                                                                    goals=goals)
            
            if quick:
                if summary_list == None:
                    return None
                return avg_list
            
            
            
            if quantifier_list != None and len(quantifier_list) > 0:
                index = best_quantifier_index(quantifier_list,t1_list)
                summary = summary_list[index]
                summarizers_list = summarizers_list[index]
                truth = t1_list[index]
                average = avg_list[index]
                #input(summarizers_list)
                
                if constraint:
                    return summarizers_list, average                
            
                length = get_summary_length(len(summarizers_list))
                simplicity = get_simplicity(len(summarizers_list)+len(flag_)+1)
                query_ = [["qualifier",flag_,summarizers,alphabet_list],["through",0,7]]
                                
                tmp = []
                for item in past_tw_list:
                    tmp.append(item[start_day:end_day])
                    
                #print(start_day,end_day)
                #input(past_tw_list)
                    
                t2 = degree_of_imprecision(avg_list)
                t3, coverage = degree_of_covering(key_list,tmp,summarizers_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_)
                t4 = degree_of_appropriateness(key_list,tmp,summarizers_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level) 
                
                summaries.append(summary)
                truth_list.append(truth)
                t2_list.append(t2)
                t3_list.append(t3)
                coverage_list.append(coverage)
                t4_list.append(t4)
                length_list.append(length)
                simplicity_list.append(simplicity)
                summarizers_lists.append(summarizers_list)
                
    if len(summaries) == 0:
        return [None]*10
    
    if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
    
    return [summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, flag_,summarizers_lists]
                
def generateEC(attr,key_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,age=None,activity_level=None,arm_filepath=None):
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
            comparison_summary, summarizer_list, goal_list = comparison_TW_SAX_summary(summarizer_type,key_list,prev_tw_letters,past_tw_letters,TW,letter_map_list,first_index+1,second_index+1,flag="eval")
            
            if comparison_summary != None:
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
                                    
                query_ = [["current index",[0,1]]]
                flag_ = "compare"
                if attr == "Heart Rate":
                    flag_ = "compareHR"
                
                tmp = []
                for i in range(len(key_list)):
                    tmp_str = ""
                    tmp_str += tw_sax_list[i][prev_]
                    tmp_str += tw_sax_list[i][past_]
                    tmp.append(tmp_str)
                                        
                t3, coverage = degree_of_covering(key_list,tmp,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag_)
                t4 = degree_of_appropriateness(key_list,tmp,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)  
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
                
                return [comparison_summary, t3, coverage, t4, length, simplicity]
            
    return [None]*6

def generateGC(attr,attr_list,key_list,data_list,sax_list,tw_sax_list,alpha,alpha_sizes,letter_map_list,TW,tw,prev_start_day,start_day,end_day,age=None,activity_level=None,day_list=None,arm_filepath=None):
    weather_flag = False
    for attr_ in attr_list:
        if "temperature" in attr_ or attr_ == "Average Temperature" or "close value" in attr_:
            weather_flag = True
            break
    
    if not weather_flag and attr != "MyFitnessPalMeals":
        first_index = len(tw_sax_list[0])-2
        second_index = len(tw_sax_list[0])-1        

        summarizer_type = "Weekly Goal " 
        prev_tw_letters = []
        past_tw_letters = []    
        past_index = len(tw_sax_list[0])-1
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
            #print(prev_tw_letters,past_tw_letters)
            comparison_summary, summarizer_list, goal_list = comparison_TW_SAX_summary(summarizer_type,key_list,prev_tw_letters,past_tw_letters,TW,letter_map_list,first_index+1,second_index+1,age=age,activity_level=activity_level)

            if comparison_summary != None:
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
                
                query_ = [["current index",[0,1]]]    
                                
                flag_ = "compare"
                if attr == "Heart Rate":
                    flag_ = "compareHRGoal"  
                    
                tmp = []
                for i in range(len(key_list)):
                    tmp_str = ""
                    tmp_str += tw_sax_list[i][prev_]
                    tmp_str += tw_sax_list[i][past_]
                    tmp.append(tmp_str) 
                    
                t3, coverage = degree_of_covering(key_list,tmp,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag_)
                t4 = degree_of_appropriateness(key_list,tmp,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)   
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
                
                return [comparison_summary, t3, coverage, t4, length, simplicity]
            
    return [None]*6

def generateGE(attr,attr_list,key_list,sax_list,past_tw_list,letter_map_list,alpha,alpha_sizes,TW,goals=[None],quick=False,start_day=None,end_day=None,age=None,activity_level=None,arm_filepath=None,ada_goal=None):
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
            
        input_goals = [goals]
        #print(input_goals)
        if attr == "MyFitnessPal":
            input_goals = goals
                                    
        avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizers_list,summarizer_type,key_list,past_tw_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,TW=TW,goals=input_goals,ada_goal=ada_goal)        
        
        if quantifier_list != None:
            index = best_quantifier_index(quantifier_list,t1_list)
            goal_summary = summary_list[index]
            summarizers = summarizer_list[index]
            truth = t1_list[index]
            average = avg_list[index]
            
            if quick:
                return [[goal_summary],[truth]]
            
            query_ = [["through",0,7]]
            tmp = []
            for item in past_tw_list:
                tmp.append(item[start_day:end_day])
                
            if attr == "StepUp" or attr == "MyFitnessPal" or attr == "MyFitnessPalMeals":
                
                t3, coverage = degree_of_covering(key_list,tmp,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,goals=input_goals,quantifier=quantifier_list[index])
            else:
                flag_ = None
                if attr == "Heart Rate":
                    flag_ = "HR"                            
                t3, coverage = degree_of_covering(key_list,tmp,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,goals=input_goals[0],flag=flag_)
            
            t4 = degree_of_appropriateness(key_list,tmp,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,goals=input_goals)
            
            length = get_summary_length(len(summarizers))
            simplicity = get_simplicity(len(summarizers)+1)
            t2 = degree_of_imprecision(avg_list)
            
            if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
            
            return [goal_summary, truth, t2, t3, coverage, t4, length, simplicity]
    if quick:
        return [None]*2    
    return [None]*8

def generateST(attr,key_list,data_list,letter_map_list,alpha_sizes,alpha,TW,age,activity_level,start_day=None,end_day=None,data_dict=None,arm_filepath=None,quick=False):
    import pandas as pd
    if attr != "MyFitnessPalMeals":
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
            
            if quick:
                return [[trend_summary],[truth]]
            
            tmp = []
            for item in data_list:
                tmp.append(item[start_day:end_day])
                
            t3, coverage = degree_of_covering(key_list,tmp,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,flag=None)
            t4 = degree_of_appropriateness(key_list,tmp,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level)               
            length = get_summary_length(len(summarizers))
            simplicity = get_simplicity(len(summarizers))
            t2 = degree_of_imprecision(avg_list)
            
            if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
            
            return [trend_summary, truth, t2, t3, coverage, t4, length, simplicity, trend_lists, summarizers]
        
    if quick:
        return [None]*2
    return [None]*8

def generateCB(attr,attr_list,key_list,full_sax_rep,tw_sax_list,sax_list,data_list,letter_map_list,alpha_sizes,alpha,tw,TW,age,activity_level,arm_filepath=None,quick=False,week_index=None,constraint=False):
    #tmp = []
    #for sublist in tw_sax_list:
        #if len(sublist) == tw:
            #tmp.append(sublist)
            
    #tw_sax_list = tmp
    summary_data_list = sax_list
    #input(tw_sax_list)
    
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
            if week_index != None:
                tw_index = week_index            
            
            #print(chunked_sax)
                
            [cluster_data, indices, tw_index, clusters] = series_clustering(full_sax_rep,tw_sax_list,tw,flag=chunked_sax,week_index=tw_index)
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
            
            #print(summarizer_type)
            avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(summarizers_list,summarizer_type,key_list,cluster_data,letter_map_list,alpha_sizes,alpha,tw_index=tw_index)
            
            #print(len(cluster_data[0]
                      #))
            #input(avg_list)

            extension = "In " + TW[:-1] + " " + str(tw_index+1) + ","
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
                #input([summary_data_list[i],tw_index*tw,tw_index*tw+tw])
                summary_data = summary_data_list[i][tw_index*tw:tw_index*tw+tw]
                
                attribute_ = key_list[i]
                if not temp_flag:
                    attribute_ = attribute_.lower()                                
                extension += " your " + attribute_ + " was"
                #print(summary_data)
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
                average = avg_list[index]
                
                if constraint:
                    return [summarizers,average]
                
                if quick:
                    return [cluster_summary,[truth],cluster_data]
                
                cluster_summary = extension + " " + cluster_summary
                
                query_ = [["current index", indices]]
                #print(indices)
                
                indices_ = []
                # TODO: make this multi
                #print(indices)
                
                for j in range(len(tw_sax_list)):
                    sublist = []
                    for index in indices:
                        tmp = []
                        tmp.append(tw_sax_list[j][index])
                        tmp.append(tw_sax_list[j][index+1])
                        sublist.append(tmp)
                    indices_.append(sublist)
                    
                #input(len(tw_sax_list))
                #if len(tw_sax_list) == 1:
                    #indices_ = indices_[0]
                #input(indices_)
                #indices_ = [indices_]
                
                t3, coverage = degree_of_covering(key_list,indices_,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,flag="compare")
                #input()
                t4 = degree_of_appropriateness(key_list,indices_,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag="compare")
                    
                # To count the summarizer in pattern_summarizers
                num_summarizers += len(key_list)
                length = get_summary_length(num_summarizers)
                simplicity = get_simplicity(num_summarizers+1)
                t2 = degree_of_imprecision(avg_list)
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
                return [cluster_summary, truth, t2, t3, coverage, t4, length, simplicity, tw_index, cluster_data, indices_, clusters, summarizers]
    if quick:
        return [None]*3    
    if constraint:
        return [None]*2
    return [None]*13

def generateSP(attr,key_list,cluster_data,tw_index,indices_,letter_map_list,alpha_sizes,age,activity_level,arm_filepath=None,quick=False):
    if cluster_data != None:
        
        summarizer_type = "Pattern Recognition - " 
        for i in range(len(key_list)):
            if key_list[i] == "step count":
                key_list[i] = "Step Count"      
                
            summarizer_type += key_list[i]
            if i != len(key_list)-1:
                summarizer_type += " and "         
        
        num_summarizers = 0
        first_letters = []
        second_letters = []
        for i in range(len(cluster_data)):
            first_letters.append(cluster_data[i][-1][0])
            second_letters.append(cluster_data[i][-1][1])
            
        num_summarizers = len(first_letters)
        sp_summary, summarizer_list = standard_pattern_summary(first_letters,second_letters,key_list,tw_index) 

        if quick: return sp_summary
        
        last_indices = []
        for i in range(len(indices_)):
            last_indices.append([indices_[i][-1]])
        #input(last_indices)
        
        #query_ = [["current index", [indices[-1]]]]
        t3, coverage = degree_of_covering(key_list,last_indices,summarizer_list,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,flag="compare")
        t4 = degree_of_appropriateness(key_list,last_indices,summarizer_list,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag="compare")                    
        length = get_summary_length(num_summarizers)
        simplicity = get_simplicity(num_summarizers+1)
        
        if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
        
        return [sp_summary, t3, coverage, t4, length, simplicity]
    
    return [None]*6

def generateIT(attr,key_list,sax_list,alphabet_list,letter_map_list,tw,weekday_dict,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,date_column,age,activity_level,hr_sax=None,arm_filepath=None):
    if tw > 0.04:
        summarizer_type = "If-then pattern "
        for i in range(len(key_list)):
            if key_list[i] == "step count":
                key_list[i] = "Step Count"   
                
            summarizer_type += key_list[i]
            if i != len(key_list)-1:
                summarizer_type += " and " 
        
        if attr == "Heart Rate":
            sax_list = [hr_sax]
            
        summary_list, supports, proto_cnt_, numsum_list, summarizers_list = analyze_patterns(key_list,sax_list,alphabet_list,letter_map_list,weekday_dict,tw,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt)
        #input()
        weekday_summaries, supports_, proto_cnt_, numsum_list_, summarizers_list_ = analyze_patterns(key_list,sax_list,alphabet_list,letter_map_list,weekday_dict,tw,alpha_sizes,db_fn_prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,weekdays=date_column)    
        
        if proto_cnt_ != None:
            proto_cnt = proto_cnt_
        
        if len(summary_list) != 0:
            t1_list = []
            t2_list = []
            t3_list = []
            t4_list = []
            coverage_list = []
            length_list = []
            simplicity_list = []
            
            t1_list_ = []
            t2_list_ = []
            t3_list_ = []
            t4_list_ = []
            coverage_list_ = []
            length_list_ = []
            simplicity_list_ = []
            
            for i in range(len(summary_list)):
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
                    
                _, t1 = getQForS(supports[i],None,None)
                t1_list.append(t1)
                t2_list.append(degree_of_imprecision([supports[i]]))
                t3_list.append(supports[i])
                #t4_list.append(degree_of_appropriateness(key_list,sax_list,summ_list,summarizer_type,supports[i],letter_map_list,alpha_sizes,age,activity_level))
                coverage_list.append(degree_of_coverage(supports[i]))
                length_list.append(numsum_list[i])
                simplicity_list.append(numsum_list[i]+1)
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
                    with open(arm_filepath,"a",newline='') as csvfile:
                        pid = pid_list[df_index]
                        datawriter = csv.writer(csvfile)
                        key_list_str = ""
                        #summ_str = ""
                        goal_str = ""
                        index_list = []
                        
                        summ_str = ""
                        item = summarizers_list[i]
                        for k in range(len(item)):
                            subitem = item[k]
                            for j in range(len(subitem)):
                                subsubitem = subitem[j]
                                for m in range(len(subsubitem)):
                                    summ = subsubitem[m]
                                    summ_str += summ
                                    if m != len(subsubitem)-1:
                                        summ_str += ","
                                if len(summ_str)>0 and summ_str[-1] != "_":
                                    #input([j,len(subitem)])
                                    summ_str += "_"
                            if k != len(item)-1:
                                #summ_str = summ_str.strip('_')
                                summ_str += ";"                                        
                    
                    
                        for j in range(len(key_list)):
                            key_list_str += key_list[j]
                            if j != len(key_list)-1:
                                key_list_str += ", "
                            
                        
                            
                        datawriter.writerow([pid,key_list_str+'|'+summ_str,tw,'IT',None,summ_str,None])                 
                
            for i in range(len(weekday_summaries)):
                
                summ_index = 0
                summ_list_ = []      
                while summ_index < len(key_list) and (attr == "MyFitnessPalMeals" and summ_index == 0): 
                    sublist = []  
                    for j in range(len(summarizers_list_[i])):
                        sublist += summarizers_list_[i][j][summ_index]
                    summ_list_.append(sublist)
                    summ_index += 1                
                
                _, t1 = getQForS(supports_[i],None,None)
                t1_list_.append(t1)                
                t2_list_.append(degree_of_imprecision([supports_[i]]))
                t3_list_.append(supports_[i])
                #t4_list_.append(degree_of_appropriateness(key_list,sax_list,summ_list_,summarizer_type,supports_[i],letter_map_list,alpha_sizes,age,activity_level))
                coverage_list_.append(degree_of_coverage(supports_[i]))
                length_list_.append(numsum_list_[i])
                simplicity_list_.append(numsum_list_[i]+1) 
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
                    with open(arm_filepath,"a",newline='') as csvfile:
                        pid = pid_list[df_index]
                        datawriter = csv.writer(csvfile)
                        key_list_str = ""
                        #summ_str = ""
                        goal_str = ""
                        index_list = []
                        
                        summ_str = ""
                        item = summarizers_list_[i]
                        
                        #input(summarizers_list_[i])

                        for k in range(len(item)):
                            subitem = item[k]
                            for j in range(len(subitem)):
                                subsubitem = subitem[j]
                                for m in range(len(subsubitem)):
                                    summ = subsubitem[m]
                                    summ_str += summ
                                    if m != len(subsubitem)-1:
                                        summ_str += ","
                                if len(summ_str)>0 and summ_str[-1] != "_":
                                    #input([j,len(subitem)])
                                    summ_str += "_"
                            if k != len(item)-1:
                                #summ_str = summ_str.strip('_')
                                summ_str += ";"                                        
                    
                    
                        for j in range(len(key_list)):
                            key_list_str += key_list[j]
                            if j != len(key_list)-1:
                                key_list_str += ", "
                            
                        
                            
                        datawriter.writerow([pid,key_list_str+'|'+summ_str,tw,'WIT',None,summ_str,None])                
            
            return [summary_list, summarizers_list, t1_list, t2_list, t3_list, coverage_list, length_list, simplicity_list, weekday_summaries, summarizers_list_, t1_list_, t2_list_, t3_list_, coverage_list_, length_list_, simplicity_list_, proto_cnt]
        
    output = [None]*17
    output[-1] = proto_cnt
    return output
  
def generateGIT(attr,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,arm_filepath=None):
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
                                   
        summarizer_list = []
        for i in range(len(key_list)):
            if alpha_sizes[i] == 7:
                summarizers = summarizer_7             
            if key_list[i] == "Heart Rate" or key_list[i] == "heart rate":
                summarizer_list.append(hr_summarizers)                                 
            else:
                summarizer_list.append(summarizers)      
        
        from itertools import combinations
        key_combos = []
        for i in range(len(key_list)):
            key_comb = combinations(key_list,i+1)
            key_combos.append(list(key_comb))  
        
        summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, summarizers_lists = [], [], [], [], [], [], [], [], []
        
        for key_combo in key_combos:
            for flag_ in key_combo:
                flag_ = list(flag_)          
                
                avg_list, t1_list, quantifier_list, summary_list, summarizers = generate_summaries(summarizer_list,summarizer_type,key_list,sax_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,xval="days",flag=flag_)
                
                if quantifier_list != None:
                    indices = []
                    for i in range(len(quantifier_list)):
                        if quantifier_list[i] == "all of the":
                            indices.append(i)
                    quantifier_list = [quantifier for quantifier in quantifier_list if quantifier == "all of the"]
                    
                    if len(quantifier_list) != 0:
                        index = best_quantifier_index(quantifier_list,t1_list)
                        index = indices[index]
                        summary = summary_list[index]
                        summarizers = summarizers[index]
                        truth = t1_list[index]
                        
                        query_ = [["qualifier",flag_,summarizers,alphabet_list]]
                        flag = None
                        if "Heart Rate" in key_list:
                            flag = "HR"
                        t3, coverage = degree_of_covering(key_list,sax_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=query_,flag=flag)
                        t4 = degree_of_appropriateness(key_list,sax_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag=flag)
                     
                        length = get_summary_length(len(summarizers))
                        simplicity = get_simplicity(len(flag_)+len(summarizers))
                        t2 = degree_of_imprecision(avg_list)                        
                        
                        summaries.append(summary)
                        truth_list.append(truth)
                        t2_list.append(t2)
                        t3_list.append(t3)
                        coverage_list.append(coverage)
                        t4_list.append(t4)
                        length_list.append(length)
                        simplicity_list.append(simplicity)
                        summarizers_lists.append(summarizers)
                        
        if len(summaries) != 0:
            if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
            
            return [summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, summarizers_lists]
                        
        return [None]*9

def generateDB(attr,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column,arm_filepath=None,quick=False,goals=None,constraint=False):
    weekdays = list(set(date_column))
    summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, avg_list_, summarizer_lists = [], [], [], [], [], [], [], [], [], []
    #input(weekdays)
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
        if goals != None:
            day_summarizers = ["reach","not reach"]        
           
        #input(key_list)                  
        for j in range(len(key_list)):
            
            if alpha_sizes[j] == 7:
                day_summarizers = summarizer_7              
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
                        
        #input(weekday_data_list)
        avg_list, t1_list, quantifier_list, summary_list, summarizer_list = generate_summaries(day_summ_list,summarizer_type,key_list,weekday_data_list,letter_map_list,alpha_sizes,alpha,age=age,activity_level=activity_level,xval=weekday,goals=goals)
        if summary_list != None:
            index = best_quantifier_index(quantifier_list,t1_list)
            day_summary = summary_list[index]
            summarizers = summarizer_list[index]
            truth = t1_list[index]          
            average = avg_list[index]
            
            if constraint:
                summarizer_lists.append(summarizer_list)
                avg_list_.append(average)
                continue
            
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
            
            summaries.append(day_summary)
            truth_list.append(truth)
            t2_list.append(t2)
            t3_list.append(t3)
            coverage_list.append(coverage)
            t4_list.append(t4)
            length_list.append(length)
            simplicity_list.append(simplicity)       
            
    if constraint:
        return summarizer_lists, avg_list_
            
    if len(summaries) != 0:
        
        if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
                
        return [summaries, truth_list, t2_list, t3_list, coverage_list, t4_list, length_list, simplicity_list, summarizers]
                        
    return [None]*9

def generateGA(attr,df_list,key_list,sax_list,summarizer_7,start_day,end_day,alpha,alpha_sizes,letter_map_list,alphabet_list,tw,TW,age,activity_level,date_column,arm_filepath=None):
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
                length = get_summary_length(num_summarizers)
                simplicity = get_simplicity(num_summarizers)
                
                if attr in ["Calorie Intake","Carbohydrate Intake","MyFitnessPal","StepUp","Step Count"] and arm_filepath != None:
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
                
                return [summary, length, simplicity]
            
    return [None]*3
    
def dynamic_nest(attr_list,summarizer_type,summ_list,summ_index,data,data_index,subindex_list,sublists,letter_map,alpha_size,age,activity_level,goals=None,range_dict=None):
    """
    attr_list:
    
    """
    
    if summ_index == len(summ_list):
        o_dict = dict()
        summarizers = []
        
        # Used to translate summarizers list to a string for mapping
        summ_string = ""
        for i in range(len(summ_list)):
            summarizers.append(summ_list[i][subindex_list[i]])
            
            summ_string += str(subindex_list[i])

        if summ_string not in o_dict.keys():
            o_dict[summ_string] = 0
        
        muS_list = []
        for i in range(len(summarizers)):
            daily_goal = None
            if goals != None and None not in goals:
                #print([i, data_index])
                #print(goals)
                #input()
                #print(data_index)
                #print(i,data_index)
                #print(len(goals),i,len(goals[i]),data_index)
                #print(len(goals),i,data_index,summarizers)
                #print(len(goals),i,len(goals[i]),data_index)
                try:
                    daily_goal = goals[i][data_index]
                except IndexError:
                    try:
                        daily_goal = goals[i]
                    except IndexError:
                        goals = goals[0]
                        try:
                            daily_goal = goals[i][data_index]
                        except IndexError:
                            daily_goal = goals[i]
                #print(goals[0][0])
                #print(daily_goal)
            
            #(summarizers)
            #print(i)
            #print(data[i])
            #print(data_index)
            data_point = data[i][data_index] 
            
            #input(data)
            #print(data_point)
            #if summarizer_type == "Food Preferences":
                #input(data_point)
            #input(age)
            if age != None and activity_level != None:
                muS = get_muS(attr_list[i],summarizer_type,summarizers[i],data_point,letter_map[i],alpha_size[i],age,activity_level,goal_=daily_goal,range_dict=range_dict)
            else:
                muS = get_muS(attr_list[i],summarizer_type,summarizers[i],data_point,letter_map[i],alpha_size[i],goal_=daily_goal,range_dict=range_dict)

            if range_dict != None and type(muS) is not bool:
                range_dict = muS[1]
                muS = muS[0]
            elif type(muS) is tuple:
                muS = muS[0]      
            
            muS_list.append(muS)
        
        #if summarizer_type == "Food Preferences":
            #input(muS_list)
        #if sum(muS_list) and len(muS_list)>1:
        #input(muS_list)
        cnt = 0
        for muS in muS_list:
            if not muS:
                cnt += 1
        #print(muS_list)
        #print(summ_string)
        #input(cnt)
        if cnt == 0:
            o_dict[summ_string] = min(muS_list)
        else:
            o_dict[summ_string] = 0
   
        return o_dict, range_dict
    
    else:
        output_dict = dict()
        for i in range(len(summ_list[summ_index])):
            sublist = [0]*len(summ_list[summ_index])
            tmp = sublists[:]
            tmp.append(sublist)
            #input(tmp)
            l = dynamic_nest(attr_list,summarizer_type,summ_list,summ_index+1,data,data_index,subindex_list+[i],tmp,letter_map,alpha_size,age,activity_level,goals=goals,range_dict=range_dict)
            if range_dict != None:
                range_dict = l[1]
                l = l[0] 
            else:
                l = l[0]
            #print(l)
            for key in l.keys():
                if key in output_dict.keys():
                    output_dict[key] += l[key]
                else:
                    output_dict[key] = l[key]
 
        return output_dict, range_dict

def generate_summaries(summarizer_lists,summarizer_type,attr_list,data_list,letter_map,alpha_size,alpha,TW="weeks",age=None,activity_level=None,xval="days",goals=None,flag=None,hr_letter_map=None,ada_goal=None,tw_index=None,range_dict=None):
    """
    Inputs:
    - summarizer_lists: a list of lists of relevant summarizers
    - summarizer_type: the type of summarizers
    - attr_list: the list of attributes
    - data_list: the time-series data
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size
    - alpha: value of alpha for alpha cut
    - TW: the time window (default is "the past week")
    - age: the user's age
    - activity_level: the user's activity level
    - xval: the x axis of the raw data
    - goals: list of lists of user-determined goals
    
    Outputs:
    - output_list: A list of lists containing the t1 truth values in one list, 
   and the possible quantifiers in another,  the generated summaries in a third, and their
   corresponding summarizers in the fourth
    
    Purpose: To generate the summaries based on the inputted summarizers that will
    dictate which quantifiers will be best for the sentence.
    """
    t1_list = []
    summary_list = []
    best_quantifiers = []
    summarizer_list = []
    avg_list = []

    # Error check
    if len(data_list) == 0:
        return [None,None,None,None,None]
    
    s_cut = []
    
    average_list = []
    muWg_list = []
    
    avg_dict = dict()
    #input(age)
    #if "Qualifier" in summarizer_type:
        #input(summarizer_lists)
    for i in range(len(data_list[0])):
        d, range_dict = dynamic_nest(attr_list,summarizer_type,summarizer_lists,0,data_list,i,[],[],letter_map,alpha_size,age,activity_level,goals=goals,range_dict=range_dict)  
        #if "Qualifier" in summarizer_type and len(data_list)>1:
            #input(summarizer_type)
        for key in d.keys():
            if key in avg_dict.keys():
                avg_dict[key] += d[key]
            else:
                avg_dict[key] = d[key]   
                    
    best_quantifier_list = []
    summary_list = [] 
            
    # Shrink dataset with qualifier
    if flag != None and "Arm Comparison" not in attr_list:
        a = alpha_size[0]
        if a == 7:
            summ_map = {"0" : "extremely low",
                        "1" : "very low",
                        "2" : "low",
                        "3" : "moderate",
                        "4" : "high",
                        "5" : "very high",
                        "6" : "extremely high"}
        else:
            summ_map = {"0" : "very low",
                        "1" : "low",
                        "2" : "moderate",
                        "3" : "high",
                        "4" : "very high"}
        attr_indices = []
        qual_dict = dict()
        for i in range(len(flag)):
            attr_indices.append(attr_list.index(flag[i]))
                                
        for key in sorted(avg_dict.keys()):
            cnt = 0
            qual_key = ""
            for i in range(len(attr_indices)):
                if i != 0:
                    qual_key += ", "
                qual_key += flag[cnt] + ": " + summ_map[key[attr_indices[i]]]
                cnt += 1

            cnt += 1
            if qual_key in qual_dict:
                qual_dict[qual_key] += avg_dict[key]
            else:
                qual_dict[qual_key] = avg_dict[key]
    #if ada_goal == "highcarblowfat":
        #input(avg_dict)
    #print(data_list)
    #input(avg_dict)
    for key in sorted(avg_dict.keys()):
        quotient = len(data_list[0])
        if flag != None and "Arm Comparison" not in attr_list:
            cnt = 0
            qual_key = ""
            for i in range(len(attr_indices)):
                if i != 0:
                    qual_key += ", "
                qual_key += flag[cnt] + ": " + summ_map[key[attr_indices[i]]]
                cnt += 1   
            
            quotient = qual_dict[qual_key]
            #print(qual_dict[qual_key])
        
        if quotient == 0:
            continue
        if type(quotient) is str and quotient.count('0') == len(quotient):
            continue

        avg_dict[key] = float(avg_dict[key])/float(quotient)
        best_quantifier, t1 = getQForS(avg_dict[key],alpha,TW)
        #print(xval,avg_dict)
        #print(avg_dict[key],best_quantifier,t1)       
        #if ada_goal == "highcarblowfat":
            #input(best_quantifier)        
    
        # Error check for getQForS function
        if best_quantifier == None:
            return [None,None,None,None,None]

        # Using the summarizers and their best quantifiers, summaries are generated
        #print summarizer_type, attr_list, summarizer_lists
        summarizers = []
        subsummarizer_list = []
        info_list = []
        if flag != None and "Arm Comparison" not in attr_list:
            index_list = []
            for i in range(len(key)):
                summarizers.append(summarizer_lists[i][int(key[i])])
                if attr_list[i] in flag:
                    info_list.append(summarizer_lists[i][int(key[i])])
                    index_list.append(i)
                else:
                    subsummarizer_list.append(summarizer_lists[i][int(key[i])])
            #input(summarizer_lists)       
            #input([summarizers,subsummarizer_list,summarizer_type])
                    
            if len(info_list) == 0:
                input([attr_list,i,flag])
                continue         
            elif len(info_list) == len(attr_list):
                return [None,None,None,None,None]
            else:
                summary = get_protoform(summarizer_type,attr_list,best_quantifier,subsummarizer_list,TW=TW,x_val=xval,qualifier_info=[flag,info_list,index_list],goals=goals,ada_goal=ada_goal,tw_index=tw_index)                
        else:
            
            if "Arm Comparison" not in attr_list:
                for i in range(len(key)):                
                    subsummarizer_list.append(summarizer_lists[i][int(key[i])])
            else:
                #input(summarizer_lists[0][int(key)])
                subsummarizer_list.append(summarizer_lists[0][int(key)])
                #try:
                    #tmp = summarizer_lists
                    #subsummarizer_list.append(tmp[i][int(key[i])])
                    #print(key,i,"added1:",tmp[i][int(key[i])])
                #except IndexError:
                    ##print(i,summarizer_lists,'\n',summarizer_lists[0],int(key[i]))
                    ##print("could be:",summarizer_lists[i][int(key[i])])
                    #tmp2 = tmp[0]
                    
                    #subsummarizer_list.append(tmp2[i])
                    #print(key,i,"added2:",tmp2[i])
                    #input(summarizer_lists[i][int(key[i])])
                              
            summarizers = subsummarizer_list
            #input(summarizers)
            if "Arm Comparison" in attr_list:
                #if "WIT" in flag:
                    #input(subsummarizer_list)
                summary = get_protoform(summarizer_type,attr_list,best_quantifier,subsummarizer_list,TW=TW,x_val=xval,qualifier_info=flag,goals=goals,ada_goal=ada_goal,tw_index=tw_index)
            else:
                summary = get_protoform(summarizer_type,attr_list,best_quantifier,subsummarizer_list,TW=TW,x_val=xval,goals=goals,ada_goal=ada_goal,tw_index=tw_index)
        
        #if ada_goal == "highcarblowfat":
        if len(summary) == 0:
            return [None,None,None,None,None]
        #elif quick:
                        
        #input([avg_dict,summarizers,key])
        avg_list.append(avg_dict[key])
        summarizer_list.append(summarizers)
        summary_list.append(summary)
        t1_list.append(t1)
        best_quantifiers.append(best_quantifier)     
        
    output_list = [avg_list,t1_list,best_quantifiers,summary_list,summarizer_list]
    #input(output_list)
    if range_dict != None:
        #input(range_dict)
        output_list.append(range_dict)
    #print(output_list)
    #input(avg_dict)
    #input([summary_list,avg_list])
    return output_list
            
def get_muS(attr,summarizer_type,summarizer,value,letter_map,alpha_size,age=None,activity_level=None,goal_=None,flag=None,range_dict=None):
    """
    Inputs: 
    - summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - summarizer: the summarizer
    - value: the value obtained from the database
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size
    - age: the user's age
    - activity_level: the user's activity level
    
    Outputs: The membership function value of the summarizer based on the
    inputted value and the summarizer type; -1 if summarizer_type is not found
    
    Purpose: To find and return the membership function value of the summarizer
    based on the inputted value and the summarizer type
    """     
    #input(summarizer_type)
    #input(attr)
    #input(value)
    #print("here",goal_,summarizer_type)
    if summarizer_type == "Step Count":
        if summarizer == "reached":
            return int(value >= 10000)
        else:          
            return int(value < 10000)
    elif summarizer_type == "Heart Rate":
        if summarizer == "reached":
            return int(hr_evaluation(value,age,activity_level) == "within range")
        else:
            return int(hr_evaluation(value,age,activity_level) != "within range")
    elif summarizer_type == "Calorie Intake":
        goal = 2000
        if goal_ != None:
            goal = goal_
        if summarizer == "reached":
            return int(value < goal)
        else:
            return int(value >= goal)  
    elif summarizer_type == "Carbohydrate Intake":
        ub = 325
        lb = 225
        
        if goal_ != None:
            goal = goal_
        if summarizer == "reached":
            return int((value <= ub) and (value >= lb))
        else:
            return int((value > ub) or (value < lb))   
    #elif summarizer_type == "Protein Intake":
        #weight = 190
        
        #if goal_ != None:
            #goal = goal_
            
        #return int(value >= 0.8*weight)
    elif summarizer_type == "Stock":
        if summarizer == "reached":
            return int(value >= 200)
        else:
            return int(value < 200)    
    elif attr == "Arm Comparison":
        #print(summarizer,value)
        return int(summarizer == value)
    elif "Trends" in summarizer_type:
        #if "doc" in summarizer_type:
            #input([summarizer,value])
        #print(value,summarizer)
        if summarizer == "increases":
            return int(value > 0)
        elif summarizer == "decreases":
            return int(value < 0)
        else:
            return int(value == 0)
    elif "Past Daily TW" in summarizer_type:
        # Handles unique data
        if "Heart Rate" in summarizer_type:
            #input(value)
            return float(hr_get_muS(summarizer,value,age,activity_level))
        elif "Activity" in summarizer_type:
            return int(categ_eval(value) == summarizer)       
        elif "Breakfast" in summarizer_type:
            #result = 1
            result = 0
            #print(value)
            
            if type(value) is dict:
                
                for key in value.keys():
                    
                    if key == "Total":
                        result = result and (value[key] <= 150)  
                        #if value[key] <= 150:
                            #result += 0.25
                    else:
                        result = result and (value[key] >= 25 and value[key] <= 50)  
                        #if value[key] >= 25 and value[key] <= 50:
                            #result += 0.25                        
                
                if summarizer == "had":
                    return (result == 1)
                else:
                    return (result == 0)
            else:
                if summarizer == "had":
                    return (value == "c")
                else:
                    return (value == "i")
        elif "Food Items" in summarizer_type:
            if summarizer == "eaten":
                return int(int(value) == 1)
            else:
                return int(int(value) == 0)
            #return int(value)
        elif letter_map == None:
            carb = False
            fat = False
            #print([value,goal_])
            if attr == "Carbohydrate Intake":
                percentage = (float(value*4)/goal_) * 100
                carb = True
            if attr == "Fat Intake":
                percentage = (float(value*9)/goal_) * 100
                fat = True             
                
            #print(attr,percentage)
                
            if summarizer == "reached":
                if carb:
                    return (percentage >= 25 and percentage <= 35)
                if fat:
                    return (percentage >= 15 and percentage <= 25)
            else:
                if carb:
                    return not (percentage >= 25 and percentage <= 35)
                if fat:
                    return not (percentage >= 15 and percentage <= 25)
        #print(evaluateSAX(value,letter_map,alpha_size),summarizer)
        return int(evaluateSAX(value,letter_map,alpha_size) == summarizer)
    elif "Pattern Recognition" in summarizer_type:
        #print(value)
        if summarizer == "rose":
            return int(value[0] < value[1])
        elif summarizer == "dropped":
            return int(value[0] > value[1])
        else:
            return int(value[0] == value[1])
    elif "Day-based" in summarizer_type: 
        if "Heart Rate" in summarizer_type:
            return float(hr_get_muS(summarizer,value,age,activity_level))
        elif "ActivFit" in summarizer_type:
            return int(categ_eval(value) == summarizer)  
        elif "Breakfast" in summarizer_type:
            return int(carb_evaluation(value) == summarizer)
        elif letter_map == None:
            carb = False
            fat = False
            if attr == "Carbohydrate Intake":
                percentage = (float(value*4)/goal_) * 100
                carb = True
            if attr == "Fat Intake":
                percentage = (float(value*9)/goal_) * 100
                fat = True   
                
            #print(percentage)
                
            if summarizer == "reach":
                if carb:
                    return (percentage >= 25 and percentage <= 35)
                if fat:
                    return (percentage >= 15 and percentage <= 25)
            else:
                if carb:
                    return not (percentage >= 25 and percentage <= 35)
                if fat:
                    return not (percentage >= 15 and percentage <= 25)            
        return int(evaluateSAX(value,letter_map,alpha_size) == summarizer)
    elif "Weekly" in summarizer_type:
        #print(summarizer_type)
        if "Heart Rate" in summarizer_type:
            return float(hr_get_muS(summarizer,value,age,activity_level))
        else:
            return int(evaluateSAX(value,letter_map,alpha_size) == summarizer)
    elif "Goal Evaluation" in summarizer_type: # TODO: fix this
        #print(attr,goal_)
        if attr == "Heart Rate":
            #input(age)
            if summarizer == "reached":
                return int(hr_evaluation(value,age,activity_level) == "within range")
            else:
                return int(hr_evaluation(value,age,activity_level) != "within range")
        if "ADA" in summarizer_type:
            if goal_ != None and "fat percentage" in goal_ and attr == "Fat Intake": # 9 calories per gram
                calories = goal_[1]
                fat = goal_[2]
                percentage = (float(fat*9)/calories) * 100
                #print(calories,fat*9,percentage)
                
                range_dict["DG25"]["Fat"].append(percentage)
                
                if summarizer == "reached":
                    return [(percentage >= 20 and percentage <= 35),range_dict]
                else:
                    return [(percentage < 20 or percentage > 35),range_dict]
            elif goal_ != None and "highcarblowfat" in goal_:
                calories = goal_[1]
                carbs = goal_[2]
                fat = goal_[3]
                
                fat_percentage = (float(fat*9)/calories) * 100
                carb_percentage = (float(carbs*4)/calories) * 100
                
                try:
                    range_dict["DG05"]["Fat"].append(fat_percentage)
                    range_dict["DG05"]["Carbohydrates"].append(carb_percentage)
                except:
                    pass
       
                if summarizer == "reached":
                    return [((fat_percentage >= 15 and fat_percentage <= 25) and (carb_percentage >= 25 and carb_percentage <= 35)),range_dict]
                else:                
                    return [(not ((fat_percentage >= 15 and fat_percentage <= 25) and (carb_percentage >= 25 and carb_percentage <= 35))),range_dict]
            elif goal_ != None and "lowcarb" in goal_: # 4 calories per gram                
                calories = goal_[1]
                carbs = goal_[2]
                percentage = (float(carbs*4)/calories) * 100
                
                range_dict["DG17"]["Carbohydrates"].append(percentage)
                
                if summarizer == "reached":
                    return [(percentage <= 45),range_dict]
                else:
                    return [(percentage > 45),range_dict]  
            elif attr == "Energy Deficit":
                return (value >= 500 and value <= 750)
            elif attr == "MyFitnessPalMeals" and "consistentcarb" in goal_:
                #input(goal_)
                #print(value,summarizer)
                
                key = goal_[1]
                #input([key,int(value),summarizer])
                if summarizer == "reached":
                    if key == "Total":
                        return (value <= 150)
                    else:
                        #return (value >= 25 and value <= 50) 
                        return (int(value) == 30)
                elif summarizer == "too low":
                    #return (value < 25)
                    return (value < 30)
                elif summarizer == "too high":
                    #return (value > 50)
                    return (value > 30)
                else:
                    #return (value >= 25 and value <= 50)   
                    return (int(value) == 30)
        
                
            
        elif attr == "Carbohydrate Intake":
            ub = 325
            lb = 225
            if summarizer == "reached":
                return ((value <= ub) and (value >= lb))
            else:
                return ((value > ub) or (value < lb))
        elif attr == "Calorie Intake":
            if summarizer == "reached":
                return (value <= 2000)
            else:
                return (value > 2000)  
        elif attr == "Fat Intake":
            ub = 77
            lb = 44
            if summarizer == "reached":
                return ((value <= ub) and (value >= lb))
            else:
                return ((value > ub) or (value < lb)) 
        elif attr == "Protein Intake":
            if summarizer == "reached":
                return (value >= 150)
            else:
                return (value < 150)   
        elif attr == "Sodium Intake":
            if summarizer == "reached":
                return (value <= 2300)
            else:
                return (value > 2300)       
        elif attr == "Sugar Intake":
            if summarizer == "reached":
                return (value <= 50)
            else:
                return (value > 50)          
        elif attr == "Step Count":
            goal = 10000
            if goal_ != None:
                #print(goal_)
                goal = goal_
            #print(value)
            #print("here2",goal_)
            #if goal == 10000:
                #input(goal_)
            if summarizer == "reached":
                return int(value >= goal)
            else:          
                return int(value < goal)      
        elif attr == "Activity":
            return -1
        elif attr == "Cue":
            if goal_ == "10 minute":
                cnt = 0
                for i in range(len(value)):
                    item = value[i]
                    
                    start_date = item[0]
                    end_date = item[1]
                    habit_time = item[2]
                    
                    diff_date = str(end_date - start_date)
                    split_date = diff_date.split(':')
                    #minutes = int(split_date[1])
                    minutes = int(round(float(split_date[1])+float(split_date[2])/60))
                    #if summarizer == "reached":
                        #return int(minutes >= 10)
                    #else:          
                        #return int(minutes < 10)   
                    cnt += int(minutes >= 10)
                    
                    #if minutes >= 10:
                        #print(item)
                
                if summarizer == "reached":
                    return int(cnt > 0)
                else:          
                    return int(cnt == 0)                   
            elif goal_ == "destination":
                start_date = value[0]
                end_date = value[1]
                habit_time = value[2]
                
                input(value)
        else:
            print(attr,goal_)
            input([attr,summarizer_type])
            input("Need to add attr")
    elif "If-then pattern" in summarizer_type:
        if type(alpha_size) == list:
            a = alpha_size[0]
        else:
            a = alpha_size
            
        if a == 7:
            reverse_letter_map = {"extremely low" : "a",
                                  "very low" : "b",
                                  "low" : "c",
                                  "moderate" : "d",
                                  "high" : "e",
                                  "very high" : "e",
                                  "extremely high" : "f"}        
        elif a == 3:
            reverse_letter_map = {"low" : "a",
                              "moderate" : "b",
                              "high" : "c"}            
        else:
            reverse_letter_map = {"very low" : "a",
                              "low" : "b",
                              "moderate" : "c",
                              "high" : "d",
                              "very high" : "e"}
        cnt = 0
        for i in range(len(value)):
            #print(value,summarizer,flag)
            #try:
                #print(reverse_letter_map[summarizer[i]],value[i])
            #except KeyError:
                #print(weekday_map[summarizer[i]],value[i])
            if summarizer[i] in reverse_letter_map.keys() and reverse_letter_map[summarizer[i]] == value[i]:
                cnt += 1
            elif summarizer[i] in weekday_map.keys() and str(weekday_map[summarizer[i]]) == value[i]:
                cnt += 1 
        
        #print(cnt,len(value))
        return (cnt == len(value))
    elif "Food Preferences" in summarizer_type:
        return value
    return -1

def get_muQ(quantifier,x):
    """
    Inputs: 
    - (DEPRECATED) summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - quantifier: the quantifier dictating which membership function to use
    - x: the value of the proportion after average of the muS
    
    Outputs: Returns the truth value of the summary based on Zadeh's calculus; -1
    if summarizer_type not found
    
    Purpose: To calculate the truth value of the summary based on Zadeh's calculus
    """
    if quantifier == "none of the" or quantifier == "not as good" or quantifier == "not":
        if x >= 0 and x <= 0.01:
            return -100*x + 1
        else:
            return 0        
        
    elif quantifier == "almost none of the":
        if x > 0 and x <= 0.01:
            return 100*x
        elif x > 0.01 and x <= 0.2:
            return 1
        elif x > 0.2 and x < 0.3:
            return -10*x + 3
        else:
            return 0               
        
    elif quantifier == "some of the":
        if x > 0.1 and x <= 0.3:
            return 5*x - 0.5
        elif x > 0.3 and x <= 0.4:
            return 1
        elif x > 0.4 and x < 0.5:
            return -10*x + 5
        else:
            return 0  
        
    elif quantifier == "half of the":
        if x > 0.4 and x < 0.5:
            return 10*x - 4
        elif x == 0.5:
            return 1
        elif x > 0.5 and x < 0.6:
            return -10*x + 6
        else:
            return 0         
        
    elif quantifier == "more than half of the":
        if x > 0.5 and x <= 0.6:
            return 10*x - 5
        elif x > 0.6 and x <= 0.75:
            return 1
        elif x > 0.75 and x < 1:
            return -4*x + 4
        else:
            return 0          
        
    elif quantifier == "most of the":
        if x > 0.5 and x <= 0.75:
            return 4*x - 2
        elif x > 0.75 and x <= 0.99:
            return 1
        elif x > 0.99 and x < 1:
            return -100*x + 100
        else:
            return 0
            
    elif quantifier == "all of the":
        if x > 0.99 and x < 1:
            return 100*x - 99
        elif x == 1:
            return 1
        else:
            return 0
        
    elif quantifier == "slightly":
        if x > 0 and x <= 0.01:
            return 100*x
        elif x > 0.01 and x <= 0.3:
            return 1
        elif x > 0.3 and x < 0.4:
            return -10*x + 4  
        else:
            return 0
        
    elif quantifier == "moderately":
        if x > 0.3 and x <= 0.4:
            return 10*x - 3
        elif x > 0.4 and x <= 0.6:
            return 1
        elif x > 0.6 and x < 0.7:
            return -10*x + 7
        else:
            return 0        
            
    elif quantifier == "considerably":
        if x > 0.6 and x <= 0.7:
            return 10*x - 6
        elif x > 0.7 and x <= 0.9:
            return 1
        elif x > 0.9 and x < 1:
            return -10*x + 10
        else:
            return 0        
        
    elif quantifier == "very":
        if x > 0.9 and x < 1:
            return 10*x - 9
        elif x == 1:
            return 1
        else:
            return 0
    
    return -1

def get_muWg(data,summarizer_type,summarizer,query):
    """
    Not yet implemented.
    """
    pass

def getQForS(value,alpha,TW,q_list=None):
    """
    Inputs:
    - (DEPRECATED) summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - value: the x for muQ(x)
    - alpha: value of alpha for alpha cut
    
    Outputs: the quantifier
    
    Purpose: to return the quantifier based on the inputted value
    """
    if q_list == None:
        q_list = ["all of the","most of the","more than half of the", "half of the","some of the","almost none of the","none of the"]

    max_truth = 0
    best_q = None
    for q in q_list:
        truth = get_muQ(q,value)
        if truth > max_truth:
            max_truth = truth
            best_q = q
            
    return best_q, max_truth

####### SAX SUMMARY FUNCTIONS #######

def get_single_SAX_summary(attr_list,letter_list,letter_map_list,alpha_sizes,TW,tw_size=None,past_tw=None,age=None,activity_level=None):
    '''
    Inputs: 
    - summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - attr_list: the list of attributes
    - letter: the list of letters representing the past time window for each attribute
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size
    - TW: the time window size 

    Outputs a summary using a specific protoform for standard evaluation summaries
    at the TW granularity
    
    Purpose: Evaluating a single SAX letter and using it to produce a standard
    evaluation summary at the TW granularity
    '''
    conclusion_list = []
    for i in range(len(attr_list)):
        if attr_list[i] == "Heart Rate":
            past_tw = past_tw[i]
            hr = sum(past_tw)/tw_size
            conclusion, summary = HR_Summary(hr,age,activity_level,TW)
        else:
            conclusion = evaluateSAX(letter_list[i],letter_map_list[i],alpha_sizes[i])
        conclusion_list.append(conclusion)
        
    if "Step Count" in attr_list:
        index = attr_list.index("Step Count")
        attr_list[index] = "step count"
        
    nutrients = ["Calories","Carbohydrates","Fat","Protein","Sodium","Sugar"]
    summary = "In the past full " + TW + ", "
    particle = "your"
    weather_flag = False
    for attr in attr_list:
        if "close value" in attr:
            weather_flag = True
            break
    
    if weather_flag:
        particle = "the"
    for i in range(len(attr_list)):         
        extra = ""
        if attr_list[i] in nutrients and "intake" not in attr_list[i].lower():
            extra = " intake"
        
        attribute_ = attr_list[i]
        if not weather_flag:
            attribute_ = attribute_.lower()
        #input(attribute_)
        summary += particle + " " + attribute_ + extra + " has been " + conclusion_list[i]
        if i == len(attr_list)-1:
            summary += "."
        elif len(attr_list) == 2 and i == 0:
            summary += " and "
        elif len(attr_list) > 2:
            summary += ", "
            if i == len(attr_list)-2:
                summary += "and "
        
    return (summary,conclusion_list)

def comparison_sTW_SAX_summary(summarizer_type,attr,prev_sax,past_sax,TW,other_tw_index=None,tw=None):
    letter_map = {"a" : 0,
                      "b" : 1,
                      "c" : 2,
                      "d" : 3,
                      "e" : 4}    
    summarizer = None
    goal = None    

    if attr == "Stock" or attr == "Step Count":    
        goal = "high"
        
    elif attr == "Calorie Intake" or attr == "Carbohydrates" or "Calories" in attr:
        goal = "low"    
        
    prev_total = 0
    past_total = 0
    
    for i in range(len(prev_sax)):
        prev_total += letter_map[prev_sax[i]]
        past_total += letter_map[past_sax[i]]
        
    if goal == "high":
        if prev_total < past_total:
            summarizer = "better"
        elif prev_total == past_total:
            summarizer = "about the same"
        else:
            summarizer = "not do as well"   
    elif goal == "low":
        if prev_total < past_total:
            summarizer = "not do as well"
        elif prev_total == past_total:
            summarizer = "about the same"
        else:
            summarizer = "better"   
            
    if summarizer == None:
        return None
            
    if other_tw_index != None and tw != None:
        return "You did " + summarizer.lower() + " with keeping your " + attr.lower() + " " + goal + " than you did on the " + TW[:-1] + " starting on day " + str(tw*other_tw_index) + "."
    
    return "You did " + summarizer.lower() + " with keeping your " + attr.lower() + " " + goal + " than you did the " + TW[:-1] + " before."        
    
def comparison_TW_SAX_summary(summarizer_type,attr_list,prev_letters,curr_letters,TW,letter_map,first_index,second_index,tw=None,flag=None,age=None,activity_level=None):
    '''
    Inputs:
    - summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - attr: the attribute
    - prev_letter: SAX letter representing the TW before the current TW
    - curr_letter: SAX letter representing the most recent TW
    - TW: the time window
    - other_tw_index: index in the data for other TWs in the data for comparison
    - tw: the time window size
    
    Outputs a comparison summary given the inputs
    
    Purpose: used to output comparison summaries
    '''
    #print(prev_letters,curr_letters)
    goal_list, summarizer_list = compare_SAX(attr_list,prev_letters,curr_letters,summarizer_type,letter_map,flag=flag,age=age,activity_level=activity_level) 
    
    #print(goal_list)
    #print(summarizer_list)

    if "Step Count" in attr_list:
        index = attr_list.index("Step Count")
        attr_list[index] = "step count"  
        
    if len(attr_list) > 1:
        identifier = "they were"
    else:
        identifier = "it was"
    
    
    if flag == "eval":
        summary = ""
        particle = "your"
        weather_flag = False
        stock_flag = False
        for attr in attr_list:
            if "Wind Speed" in attr or "Temperate" in attr:
                weather_flag = True
                break
            if "close value" in attr:
                stock_flag = True
                break
        
        #print(weather_flag, attr)
        if weather_flag or stock_flag:
            particle = "the"
        for i in range(len(attr_list)):
            if i == 0:
                first = particle.capitalize() + " "
            else:
                first = particle + " "
                
            attribute_ = attr_list[i]
            if not stock_flag:
                attribute_ = attribute_.lower()            
                
            summary += first + attribute_ + " was " + summarizer_list[i] 
            
            if i == len(attr_list)-1:
                summary += " in " + TW[:-1] + " " + str(second_index)
                if summarizer_list[i] == "about the same":
                    summary += " as "
                else:
                    summary += " than "
            
            if i != len(attr_list)-1:
                summary += " and "

        #if first_index != None and second_index != None:
        summary += identifier + " in " + TW[:-1] + " " + str(first_index) + "."
        #else:        
            #summary += identifier + " the " + TW[:-1] + " before."
            
        return summary, summarizer_list, goal_list
            
    if len(summarizer_list) == 0 or None in summarizer_list:
        return None,None,None
        
    summary = ""
    for i in range(len(attr_list)):
        if i == 0:
            first = "You did "
        else:
            first = "you did "
            
        summary += first + summarizer_list[i] + " overall with keeping your " + attr_list[i].lower() + " " + goal_list[i]
        
        if i == len(attr_list)-1:
            summary += " in " + TW[:-1] + " " + str(second_index)        
        
        if i != len(attr_list)-1:
            summary += " and "
            
    #if other_tw_index != None:
    summary += " than you did in " + TW[:-1] + " " + str(first_index) + "."
    #else:        
        #summary += " than you did the " + TW[:-1] + " before."    
        
    return summary, summarizer_list, goal_list

####### OTHER SAX FUNCTIONS #######

def letter_dist(q_i,c_i):
    '''
    Inputs:
    - q_i: first letter
    - c_i: second letter
    
    Outputs the distance between the two letters
    
    Purpose: calculates the distance between the two letters
    '''
    # Breakpoints for alphabet size=5
    breakpoints = [-0.84,-0.25,0.25,0.84]
    
    lookup_table = []
    for r in range(5):
        row = []
        for c in range(5):
            if abs(r-c) <= 1:
                row.append(0)
            else:
                val = breakpoints[max(r,c)-1] - breakpoints[min(r,c)]
                row.append(val)
        lookup_table.append(row)
        
    letter_map = {"a" : 0,
                  "b" : 1,
                  "c" : 2,
                  "d" : 3,
                  "e" : 4}
    
    return lookup_table[letter_map[q_i]][letter_map[c_i]]

def summarizer_to_SAX(summarizer,alpha_size,attr=None):
    if alpha_size == 5:
        if attr == "Heart Rate":
            reverse_summ_map = {'abnormally low' : 'a',
                                'low' : 'l',
                                'within range' : 'w',
                                'high' : 'h',
                                'abnormally high' : 'b'}
        else:
            reverse_summ_map = {'very low' : 'a',
                                'low' : 'b',
                                'moderate' : 'c',
                                'high' : 'd',
                                'very high' : 'e'}
    elif alpha_size == 7:
        reverse_summ_map = {'extremely low' : 'a',
                            'very low' : 'b',
                            'low' : 'c',
                            'moderate' : 'd',
                            'high' : 'e',
                            'very high' : 'f',
                            'extremely high' : 'g'}
    
    return reverse_summ_map[summarizer]
    

def evaluateSAX(letter,letter_map,alpha_size,flag=None):
    '''
    Inputs:
    - letter: the letter representing the time window
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size
    - flag: flag to handle unique data
    
    Outputs summarizer that the letter is mapped to
    
    Purpose: to convert a letter to a summarizer for evaluation
    '''
    
    # Mappings that enumerate the summarizers used based on alphabet size
    # Enumeration resembles buckets
    summarizer_5_map = {1 : "very low",
                          2 : "low",
                          3 : "moderate",
                          4 : "high",
                          5 : "very high"}     
    
    summarizer_7_map = {1 : "extremely low",
                        2 : "very low",
                          3 : "low",
                          4 : "moderate",
                          5 : "high",
                          6 : "very high",
                          7 : "extremely high",}     
    
    summarizer_3_map = {1 : "low",
                        2 : "moderate",
                        3 : "high"}       
        
    summarizer_2_map = {1 : "low",
                        2 : "high"}    
    
    value = letter_map[letter]
    
    # Different mappings for different summarizers
    if flag == "HR":
        summarizer_map = {1 : "abnormally low",
                          2 : "low",
                          3 : "within range",
                          4 : "high",
                          5 : "abnormally high"} 
        return summarizer_map[value]
    
    if flag == "ACT":
        summarizer_map = {
            1 : "walking",
            2 : "inactive",
            3 : "in a vehicle"
        }
        return summarizer_map[value]
    
    if flag == "CC":
        summarizer_map = {
            1 : "consistent",
            2 : "inconsistent"
        }
        return summarizer_map[value]
    
    # Choose bucket the value fits in 
    summarizer_map = None
    if alpha_size  == 2:
        summarizer_map = summarizer_2_map
    elif alpha_size == 3:
        summarizer_map = summarizer_3_map    
    elif alpha_size == 5:
        summarizer_map = summarizer_5_map  
    elif alpha_size == 7:
        summarizer_map = summarizer_7_map      
            
    bucket_size = alpha_size/len(summarizer_map.keys())
    
    bucket = int(math.floor(float(value)/float(bucket_size)))
    
    # Handle error case
    if bucket == 0:
        bucket = 1
    
    return summarizer_map[bucket]
    

def best_quantifier_index(quantifiers,truths):
    '''
    Inputs:
    - quantifiers: the possible quantifiers of the summaries generated
    - truths: the truth values of the summaries
    
    Outputs:
    - index: the index of the best quantifier
    
    Purpose: find the best quantifier in order to determine which summary to
    generate
    '''
    
    # Mapping of possible quantifiers to an enumeration, resembling an order
    # of importance
    quant_map = {"none of the" : 1,
                 "almost none of the" : 2,
                 "some of the" : 3,
                 "half of the" : 4,
                 "more than half of the" : 5,
                 "most of the" : 6,
                 "all of the" : 7
                 }
    
    # Find the values that correspond to the quantifiers in the input list
    values = []
    for i in range(len(quantifiers)):
        values.append(quant_map[quantifiers[i]])
    
    truth = 0
    index = 0
        
    if values.count(max(values)) > 1:
        # To handle ties, factor in the truth values
        for i in range(len(values)):
            if values[i] == max(values):
                if truths[i] > truth:
                    truth = truths[i]
                    index = i
    else:
        index = values.index(max(values))
                    
    return index

####### USER EVALUATION FUNCTIONS #######

def goal_assistance(goal,values):
    '''
    Inputs: 
    - goal: the goal specified or relevant to the user
    - values: the values of measures relevant to the goal
    
    Outputs:
    - results: the results of comparing the inputted values to the goal/guideline
    requirements
    
    Purpose: a preliminary implementation of the construction of goal assistance
    summaries
    '''
    results = dict()
    
    if goal == "FSC":
        target_map = {"protein" : 50,
                          "fat" : 70,
                          "sat_fat" : 24,
                          "carbohydrates" : 310,
                          "sugar" : 90,
                          "sodium" : 2.3,
                          "fiber" : 30}   
        # Specify a need for an increase or a decrease when comparing the inputted
        # values to the goal/guideline
        for key in values.keys():
            if key in target_map:
                if values[key] < target_map[key]:
                    results[key] = "increase"
                elif values[key] > target_map[key]:
                    results[key] = "decrease"
                    
    elif goal == "2000-cal":
        between = ["Carbohydrates","Fat"]
        above = ["Protein"]
        below = ["Calorie Intake","Sodium","Sugar"]        
        
        value_map = {"Carbohydrates-u" : 325,
                     "Carbohydrates-l" : 225,
                     "Fat-u" : 77,
                     "Fat-l" : 44,
                     "Protein" : 150,
                     "Calorie Intake" : 2000,
                     "Sodium" : 2300,
                     "Sugar" : 50}
        
        for key in values.keys():
            try:
                if key in between:
                    if values[key] > value_map[key+"-u"]:
                        results[key] = "decrease"
                    elif values[key] < value_map[key+"-l"]:
                        results[key] = "increase"
                    else:
                        continue
                elif key in above:                    
                    if values[key] < value_map[key]:
                        results[key] = "increase"
                    else:
                        continue
                else:
                    #print(key)
                    #print(key in values.keys())
                    #input(values.keys())
                    
                    #input([values[key],value_map[key]])
                    if values[key] > value_map[key]:
                        results[key] = "decrease"
                    else:
                        continue
            except KeyError:
                continue
                
    return results

def HR_Summary(heart_rate, age, activity_level, TW):
    '''
    Inputs: 
    - heart_rate: the user's average heart rate
    - age: the user's age
    - activity_level: the user's activity level
    - TW: the time window (default is "the past week")
    
    Outputs a standard evaluation summary for heart rate
    
    Purpose: A separate summary generation function for heart rate
    '''
    conclusion = hr_evaluation(heart_rate, age, activity_level)
    summary = "In the past full " + TW + ", your heart rate has been " + conclusion + "."
    
    return summary, [conclusion]

def carb_evaluation(value):
    
    if type(value) is dict:
        result = 1
        for key in value.keys():
            if key == "Total":
                result = result and (value[key] <= 150)    
            else:
                #result = result and (value[key] >= 25 and value[key] <= 50)     
                result = result and (value[key] == 30)     
                
        result_map = {0 : "did not have",
                      1 : "had"}
    else:
        result = value
        result_map = {"i" : "inconsistent",
                      "c" : "consistent"}
    
    return result_map[result]
            
def hr_evaluation(heart_rate, age, activity_level):
    '''
    Inputs: 
    - heart_rate: the user's average heart rate
    - age: the user's age
    - activity_level: the user's activity level
    
    Outputs summarizers for the data based on the inputs
    
    Purpose: To retrieve summarizers for heart rate data, as it relies on a unique 
    set of summarizers
    '''
    
    if age >= 18:
        lower_bound = 60
    else:
        lower_bound = 70
    
    if type(heart_rate) is str:
        hr_letter_map = {"a" : "abnormally low",
                            "l" : "low",
                            "w" : "within range",
                            "h" : "high",
                            "b" : "abnormally high"} 
        
        return hr_letter_map[heart_rate]
    
    if heart_rate >= lower_bound and heart_rate <= 100:
        return "within range"
    
    elif heart_rate < lower_bound:
        if activity_level == "active":
            if heart_rate >= 40:
                return "within range"
            elif heart_rate < 40 and heart_rate > 30:
                return "low"
            else:
                return "abnormally low"
        else:
            if heart_rate > 50:
                return "low"
            else:
                return "abnormally low"
    else:
        if heart_rate <= 110:
            return "high"
        else:
            return "abnormally high"
        
def comparison_HR_summary(last_tw,curr_tw,age,activity_level,TW):
    '''
    Inputs:
    - last_tw: heart rate data for the time window before the past full time window
    - curr_tw: heart rate data for the past full time window
    - age: the user's age
    - activity_level: the user's activity level
    
    Outputs a comparison summary using summarizers for the heart rate
    
    Purpose: To output a comparison summary for heart rate data, as it relies on a unique 
    set of summarizers
    '''
    summarizer = compare_HR_TW(last_tw,curr_tw,age,activity_level)
        
    summary = "You did " + summarizer.lower() + " with keeping your heart rate within range than you did the " + TW + " before."
    
    return summary, summarizer


def categ_eval(letter):
    '''
    Inputs a letter for SAX representation
    
    Outputs the corresponding activity
    
    Purpose: Maps inputted letter to the activity
    '''
    activity_map = {
        "w" : "walking",
        "s" : "inactive",
        "v" : "in a vehicle"
    }
    
    return activity_map[letter]

def comparison_activ(prev_day,curr_day,other_index=None):
    '''
    Inputs:
    - prev_day: data for previous day
    - curr_data: data for past full day
    - other_index: data for another day in data (default is None)
    
    Outputs a comparison summary for activity between two days
    
    Purpose: Outputs a comparison summary for categorical activity data
    '''
    summarizer, pair_word = compareACT(prev_day,curr_day)
        
    if other_index != None:
        summary = "You were " + summarizer + " active " + pair_word + " you were on day " + str(other_index+1) + "."
    else:
        summary = "You were " + summarizer + " active " + pair_word + " you were the previous day."

    return summary, summarizer

####### SUMMARY EVALUATION FUNCTIONS #######

def hr_get_muS(summarizer,heart_rate,age,activity_level):
    '''
    Inputs: 
    - summarizer: the conclusive phrase of a summary
    - heart_rate: the user's average heart rate
    - age: the user's age
    - activity_level: the user's activity level
    
    Outputs membership function value based on inputs
    
    Purpose: To retrieve membership function values for heart rate data points
    '''
    
    if age >= 18:
        lower_bound = 60
    else:
        lower_bound = 70    
        
    if activity_level == "active":
        lower_bound = 40
        
    if summarizer == "abnormally low":

        if activity_level == "active":
            upper = 30
            slope = -1.0/10
            b = -3
        else:
            upper = 50
            slope = -1.0/30
            b = -5.0/3
            
        if heart_rate < 20:
            return 1
        elif heart_rate >= 20 and heart_rate < upper:
            return slope*heart_rate - b
        else:
            return 0
    
    if summarizer == "low":

        if activity_level == "active":
            upper = 30
            slope = 1.0/10
            b = 2
        else:
            upper = 50
            slope = 1.0/30
            b = 2.0/3
            
        if heart_rate >= 20 and heart_rate < upper:
            return slope*heart_rate - b
        elif heart_rate >= 30 and heart_rate < lower_bound:
            return 1
        else:
            return 0
        
    if summarizer == "within range":
        if heart_rate >= lower_bound and heart_rate <= 100:
            return 1
        else:
            return 0
        
    if summarizer == "high":
        if heart_rate > 100 and heart_rate <= 110:
            return 1
        elif heart_rate > 110 and heart_rate <= 120:
            return -0.1*heart_rate + 12
        else:
            return 0
        
    if summarizer == "abnormally high":
        if heart_rate > 110 and heart_rate < 120:
            return 0.1*heart_rate - 11
        elif heart_rate >= 120:
            return 1
        else:
            return 0 
        
    return -1
        
def compare_SAX(attr_list,prev_letters,curr_letters,summarizer_type,letter_map,flag=None,age=None,activity_level=None):
    goal_list = []
    conclusion_list = []
    covered = []
    
    temp_flag = False
    index_list = []
    if type(attr_list) is list:
        for j in range(len(attr_list)):
            if "temperature" in attr_list[j] or attr_list[j] == "Average Temperature":
                temp_flag = True
                index_list.append(j)  
    else:
        if "temperature" in attr_list or attr_list == "Average Temperature":
            temp_flag = True
            index_list.append(0)  
            
    #print(attr_list)
    
    #print(prev_letters,curr_letters)
    
    for i in range(len(prev_letters)):
        goal = None
        conclusion = None
        prev_letter = prev_letters[i]
        curr_letter = curr_letters[i]
        
        #print(prev_letter,curr_letter)
        
        if flag == "eval":
            if prev_letter < curr_letter:
                conclusion = "higher"
            elif prev_letter == curr_letter:
                conclusion = "about the same"
            else:
                conclusion = "lower"     
                
            goal_list.append(None)
            conclusion_list.append(conclusion)
            continue
        
        if temp_flag and i in index_list:
            if prev_letter < curr_letter:
                conclusion = "better"
            elif prev_letter == curr_letter:
                conclusion = "about the same"
            else:
                conclusion = "not do as well"     
                
            goal_list.append(None)
            conclusion_list.append(conclusion)
            continue            
            
    
        # Goals help identify what is "better" or "worse" in terms of comparison for the attribute    
        if "close" in summarizer_type and "close" not in covered:    
            goal = "high"
            covered.append("close value")
            
        elif "Step Count" in summarizer_type and "Step Count" not in covered:
            goal = "high"
            covered.append("Step Count")
            
        elif "Calorie Intake" in summarizer_type and "Calorie Intake" not in covered:
            goal = "low"  
            covered.append("Calorie Intake")
        
        elif "Carbohydrate Intake" in summarizer_type and "Carbohydrate Intake" not in covered:
            goal = "low"          
            covered.append("Carbohydrate Intake")    
        
        elif "Calories" in summarizer_type and "Calories" not in covered:
            goal = "low"          
            covered.append("Calories")
            
        elif "Fat Intake" in summarizer_type and "Fat Intake" not in covered:
            goal = "low"
            covered.append("Fat Intake")
            
        elif "Protein" in summarizer_type and "Protein" not in covered:
            goal = "high"
            covered.append("Protein")    
            
        elif "Sodium" in summarizer_type and "Sodium" not in covered:
            goal = "low"
            covered.append("Sodium")   
                        
        elif "Sugar" in summarizer_type and "Sugar" not in covered:
            goal = "low"
            covered.append("Sugar")                        
            
        elif "Heart Rate" in summarizer_type and "Heart Rate" not in covered:
            goal = "within range"
            covered.append("Heart Rate")
            
        elif "Activity" in summarizer_type and "Activity" not in covered:
            goal = "active"
            covered.append("Activity") 
            
        if "Pattern Recognition" in summarizer_type and "Pattern Recognition" not in covered:
            goal = "cluster"
            covered.append("Pattern Recognition")
                        
        #print(summarizer_type)
        if goal == None:
            return [],[]
        
        if goal == "high":
            if prev_letter < curr_letter:
                conclusion = "better"
            elif prev_letter == curr_letter:
                conclusion = "about the same"
            else:
                conclusion = "not do as well"   
        elif goal == "low":
            if prev_letter < curr_letter:
                conclusion = "not do as well"
            elif prev_letter == curr_letter:
                conclusion = "about the same"
            else:
                conclusion = "better"    
        elif goal == "within range":
            conclusion = compare_HR_TW(prev_letter,curr_letter,age,activity_level)
        elif goal == "active":
            conclusion, goal = compareACT(prev_letter,curr_letter) 
        elif goal == "cluster":
            #print(prev_letter,curr_letter,summarizer_type)
            if prev_letter < curr_letter:
                conclusion = "better"
            elif prev_letter == curr_letter:
                conclusion = "about the same"
            else:
                conclusion = "not do as well"              
        
        goal_list.append(goal)
        conclusion_list.append(conclusion)
            
    #print(goal_list,conclusion_list)
    return goal_list, conclusion_list

def compare_HR_TW(last_tw,curr_tw,age,activity_level):
    
    goal = "within range"
    c_cnt = 0
    l_cnt = 0
    #print("func",curr_tw,last_tw)
    for i in range(len(last_tw)):
        if hr_evaluation(last_tw[i],age,activity_level) == goal:
            l_cnt += 1
        if hr_evaluation(curr_tw[i],age,activity_level) == goal:
            c_cnt += 1                
    #print(c_cnt,l_cnt)
    conclusion = None
    if l_cnt > c_cnt:
        conclusion = "not do as well"
    elif l_cnt < c_cnt:
        conclusion = "better"
    else:
        conclusion = "about the same"    
        
    return conclusion

def compareACT(prev_day,curr_day):
    prev = prev_day.count("w")
    curr = curr_day.count("w")
    
    goal = "high"
    
    if prev > curr:
        summarizer = "not do as well"
    elif prev < curr:
        summarizer = "better"
    else:
        summarizer = "about the same"
        
    return summarizer, goal

def computeScore(vals):
    
    
    def getRI(n):
        if n == 3: 
            return 0.58
        if n == 4: 
            return 0.9
        if n == 5: 
            return 1.12
        if n == 6: 
            return 1.24
        if n == 7: 
            return 1.32
        if n == 8: 
            return 1.41
        if n == 9: 
            return 1.45
        if n == 10: 
            return 1.49    
        
    n = 5
    import string
    alphabet = string.ascii_uppercase
    
    degree_map = {'truth' : 'A',
                  'imprecision' : 'B',
                  'covering' : 'C',
                  'appropriateness' : 'D',
                  'coverage' : 'E'}
    
    keys = ['A','B','C','D','E']
    
    master_dict = {'A' : {'A' : 1,
                            'B' : 3,
                            'C' : 9,
                            'D' : 7,
                            'E' : 5},
                     'B' : {'A' : 0.33,
                            'B' : 1,
                            'C' : 7,
                            'D' : 5,
                            'E' : 3},
                     'C' : {'A' : 0.11,
                            'B' : 0.14,
                            'C' : 1,
                            'D' : 0.33,
                            'E' : 0.2},
                     'D' : {'A' : 0.14,
                            'B' : 0.2,
                            'C' : 3,
                            'D' : 1,
                            'E' : 0.33},
                     'E' : {'A' : 0.2,
                            'B' : 0.33,
                            'C' : 5,
                            'D' : 3,
                            'E' : 1},
                     }
    
    # Create matrix
    matrix_list = []
    #vals = []
    for i in range(len(vals)):
        #key = degree_map[val[0]]
        key = keys[i]
        value = vals[i]
        #vals.append(values[i])
        
        sublist = []
        for value in master_dict[key].values():
            sublist.append(round(value,2))
        matrix_list.append(sublist)
    #master_matrix = sp.Matrix(matrix_list)
    
    #Find priority vector
    col_sums = []
    for i in range(len(matrix_list)):
        col_sum = 0
        for j in range(len(matrix_list[i])):
            col_sum += matrix_list[j][i]
        col_sums.append(col_sum)
    
    norm_matrix = []
    for i in range(len(matrix_list)):
        row = []
        for j in range(len(matrix_list[i])):
            row.append(matrix_list[i][j]/col_sums[j])
        norm_matrix.append(row)
    
    priority_vector = []
    for i in range(len(norm_matrix)):
        row_avg = sum(norm_matrix[i]) / len(norm_matrix[i])
        priority_vector.append(row_avg)
    
    # Find largest eigenvalue
    lambda_max = 0
    for i in range(len(priority_vector)):
        lambda_max += col_sums[i]*priority_vector[i]
        
    # Compute consistency index and ratio
    c_i = float(lambda_max - n)/(n - 1)
    c_r = c_i/getRI(n)
    #input(c_r)
    
    score = 0
    for i in range(len(vals)):
        for j in range(len(priority_vector)):
            score += vals[i]*priority_vector[j]
   
    return score
        
def degree_of_covering(attr_list,data_list,summarizers,summarizer_type,letter_map_list,alpha_sizes,age,activity_level,query_list=None,flag=None,goals=None,TW="weeks",quantifier=None):
    """
    Inputs: 
    - data: the portion of the database specified by the query
    - summarizers: the conclusive phrases of the summary
    - summarizer_type: the type of summarizer
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size   
    - age: the user's age
    - activity_level: the user's activity level
    - query: the query
    
    Outputs: the degree of covering
    
    Purpose: to calculate the degree of covering. This says how many objects in the database corresponding to the user's query are covered by the summary 
    
    """ 
    t_covering = []
    t_coverage = []
    h = []
    
    try:
        n = len(data_list[0])
    except TypeError:
        data_list = [data_list]
        n = len(data_list)
    #if "Pattern Recognition" in summarizer_type:
        #n = len(data_list)
        
    #print(n)
    
    for i in range(n):

        muS_list = []
        
        for j in range(len(summarizers)):
            muS = None
            #if flag == "comparePR":
                
            
            if flag == "compare":
                #print(flag)
                skip_index = 0
                #if "Pattern Recognition" in summarizer_type:
                    #skip_index = len(data_list[0])-1

                #if i == skip_index or ("Pattern Recognition" in summarizer_type and (i+1)%2==0):
                if i == skip_index and "Pattern Recognition" not in summarizer_type:
                    continue
                
                #print(j,i)
                #print(data_list)
                
                
                if "Pattern Recognition" in summarizer_type:
                    first_letter = data_list[j][i][0]
                    second_letter = data_list[j][i][1]  
                else:
                    first_letter = data_list[j][i-1]
                    second_letter = data_list[j][i]                    
                #print(first_letter,second_letter)
                
                compare_flag = "eval"
                if "Goal" in summarizer_type or "Pattern Recognition" in summarizer_type:
                    compare_flag = None
                
                goal_list, conclusion_list = compare_SAX(attr_list[j],first_letter,second_letter,summarizer_type,letter_map_list[j],flag=compare_flag)
                #print(conclusion_list, first_letter, second_letter, i)
                #print(data_list)
                conclusion = conclusion_list[0]
                
                if "Pattern Recognition" in summarizer_type:          
                    summarizer_map = { "better" : "rose",
                                       "about the same" : "stayed the same",
                                       "not do as well" : "dropped"}
                    conclusion = summarizer_map[conclusion_list[0]]
                
                #print([conclusion,summarizers[j]])
                if conclusion == summarizers[j]:
                    muS = 1
                else:
                    muS = 0 
                    
            elif flag == "compareHR":
                
                #if i == 0:
                    #continue
                #print(i)
                #if i%7 != 0 or i < 7:
                    #muS = None
                    #continue
                #print(data_list[j])
                #curr_tw = data_list[j][i:i+7]
                #last_tw = data_list[j][i-7:i]
                #curr_tw = [data_list[j][i]]
                #last_tw = [data_list[j][i-1]]
                
                if "Pattern Recognition" in summarizer_type:
                    last_tw = [data_list[j][i][0]]
                    curr_tw = [data_list[j][i][1]]
                else:
                    curr_tw = [data_list[j][i]]
                    last_tw = [data_list[j][i-1]]               
                #print([i,curr_tw,last_tw])
                
                #conclusion = compare_HR_TW(last_tw,curr_tw,age,activity_level)
                summary, conclusion, goal_list = comparison_TW_SAX_summary(summarizer_type,attr_list,last_tw,curr_tw,TW,letter_map_list,i-1,i,flag="eval")
                #print(summary,conclusion,goal_list)
                conclusion_map = { 'lower' : 'dropped',
                                   'higher' : 'rose',
                                   'about the same' : 'stayed the same'}
                
                #input([conclusion,summarizers[j]])
                #print(conclusion_map[conclusion[j]],summarizers[j])
                if conclusion_map[conclusion[j]] == summarizers[j]:
                    muS = 1
                else:
                    muS = 0
            elif flag == "compareHRGoal":               
                
                curr_tw = [data_list[j][i]]
                last_tw = [data_list[j][i-1]]
                #print(curr_tw,last_tw)
                conclusion = compare_HR_TW(last_tw,curr_tw,age,activity_level)
                #print(conclusion,summarizers[j])
                if conclusion == summarizers[j]:
                    muS = 1
                else:
                    muS = 0            
                    
            elif flag == "compareACT":
                
                if i==0:
                    continue
    
                conclusion, pair_word = compareACT(data_list[j][i-1],data_list[j][i])
                
                if conclusion == summarizers[j]:
                    muS = 1
                else:
                    muS = 0
            elif flag == "HR" or attr_list[j] == "Heart Rate":
                
                #input(data_list)
                if "Trends" in summarizer_type:
                    goal = None
                    if goals != None:
                        goal = goals[j][i]                    
                    muS = get_muS(attr_list[j],summarizer_type,summarizers[j],data_list[j][i],letter_map_list[j],alpha_sizes[j],goal_=goal) 
                else:
                    #print(hr_evaluation(data_list[j][i],age,activity_level),summarizers[j])
                    if hr_evaluation(data_list[j][i],age,activity_level) == summarizers[j]:
                        muS = 1
                    elif hr_evaluation(data_list[j][i],age,activity_level) == "within range" and summarizers[j] == "reached":
                        muS = 1
                    elif hr_evaluation(data_list[j][i],age,activity_level) != "within range" and summarizers[j] == "did not reach":
                        muS = 1
                    else:
                        muS = 0

            else:
                #print(summarizer_type)
                #print(i,goals)
                goal = None
                if goals != None and None not in goals:
                    #print(goals,j,i)
                    try:
                        goal = goals[j][i]
                    except:
                        goal = goals[j]
                #print(i,goal)
                #print(data_list[j][i], summarizer_type)
                muS = get_muS(attr_list[j],summarizer_type,summarizers[j],data_list[j][i],letter_map_list[j],alpha_sizes[j],goal_=goal) 
                #print(muS, summarizers[j])
            #print(muS_list)
            muS_list.append(muS)
        #input(muS_list)
        #print(query_list)
        if query_list == None:
            muWg = 1
        elif isinstance(query_list,list):
            final_muWg = 1
            for query in query_list:
                if query[0] == "through":
                    #print([i, query[1], query[2]])
                    if i >= query[1] and i < query[2]:
                        muWg = 1
                    else:
                        muWg = 0
                elif query[0] == "jump":
                    if i == query[1] or i == query[2]:
                        muWg = 1
                    else:
                        muWg = 0
                elif query[0] == "non-consecutive":
                    #input([i,query[1],query[2]])
                    if i in query[1] or i in query[2]:
                        muWg = 1
                    else:
                        muWg = 0
                elif query[0] == "indices":
                    index = i-1
                    if index in query[1]:
                        muWg = 1
                    else:
                        muWg = 0
                elif query[0] == "current index":
                    #if flag == "compare":
                        #input([query[0],query[1]])
                    index = i
                    
                    if index in query[1]:
                        muWg = 1
                    else:
                        muWg = 0        
                elif query[0] == "qualifier":
                    alphabet_list = query[3]
                    query_summarizers = query[2]
                    
                    qualifier_list = []
                    for k in range(len(query[1])):
                        index = attr_list.index(query[1][k])
                        qualifier_list.append([index,summarizers[index]])
                    
                    cnt = 0
                    for k in range(len(qualifier_list)):
                        index = qualifier_list[k][0]
                        if alphabet_list[index][query_summarizers.index(qualifier_list[k][1])] == data_list[index][i]:
                            cnt += 1
                            
                    if cnt == len(qualifier_list):
                        muWg = 1
                    else:
                        muWg = 0
                #print(query[0])
                
                final_muWg = int(int(final_muWg) and muWg)
            muWg = final_muWg
        else:
            muWg = get_muWg(data_list[j][i],summarizer_type,summarizers[j],query)
    
        #print(final_muWg,muWg,muS_list)
        if (muS != None):
            cnt = 0
            for muS in muS_list:
                if not muS:
                    cnt += 1
            #print(cnt)          
            if cnt == 0:
                muS_covering = min(muS_list)
                muS_coverage = 1
            else:
                muS_covering = 0
                muS_coverage = 0   
            
            #print(muS_covering,muWg)
            t_covering.append(muS_covering>0 and muWg>0)
            t_coverage.append(muS_coverage>0)
            h.append(muWg>0)
            
   
    #if sum(t_covering)==0 and quantifier != "none of the":
        #print("ERROR: t_covering is 0")
        #input()
    #input()\
    #print(len(t_covering),len(h))
    #print(sum(t_covering),sum(h))
    #print(h)
    if sum(h) == 0:
        covering = 0
    else:
        covering = float(sum(t_covering))/sum(h)
            
    r = float(sum(t_coverage))/len(data_list[0])
    
    r1 = 0.02
    r2 = 0.15
    
    if r <= r1:
        coverage = 0
    elif r1 < r and r < (r1 + r2)/2:
        coverage = 2*(((r - r1)/(r2 - r1))**2)
    elif r >= (r1 + r2)/2 and r < r2:
        coverage = 1 - 2*(((r2 - r)/(r2 - r1))**2)
    else: 
        coverage = 1
    
    return covering, coverage

def degree_of_coverage(r):
    
    r1 = 0.02
    r2 = 0.15
    
    if r <= r1:
        coverage = 0
    elif r1 < r and r < (r1 + r2)/2:
        coverage = 2*(((r - r1)/(r2 - r1))**2)
    elif r >= (r1 + r2)/2 and r < r2:
        coverage = 1 - 2*(((r2 - r)/(r2 - r1))**2)
    else: 
        coverage = 1
        
    return coverage

def degree_of_appropriateness(attr_list,data_list,summarizers,summarizer_type,t3,letter_map_list,alpha_sizes,age,activity_level,flag=None,goals=None):
    """
    Inputs: 
    - data: the database
    - summarizer: the conclusive phrase of the summary
    - summarizer_type: the type of summarizer
    - t3: the degree of covering
    - letter_map: a mapping from letters to integers
    - alpha_size: the alphabet size 
    - age: the user's age
    - activity_level: the user's activity level
    
    Outputs: the degree of appropriateness
    
    Purpose: to calculate the degree of appropriateness. The degree of appropriateness describes how characteristic for the particular database the summary found is. This helps avoid the output of trivial summaries
    """     
    # TODO: Factor this in once we have multiple attributes
       
    #t4_list = []
    # Day count    
    r_list = []
    #print(data_list)
    #input([summarizers,attr_list])
    #print("degree")
    #print(summarizers)
    try:
        n = len(data_list[0])
    except TypeError:
        data_list = [data_list]
        n = len(data_list)
    #if "Pattern Recognition" in summarizer_type:
        #n = len(data_list)    
    #print(flag)
    for j in range(len(summarizers)):
        t_k = []
        summarizer = summarizers[j]
        for i in range(n):
            #print(j,i)
            
            if flag == "compare":
                if (i == 0 and "Pattern Recognition" not in summarizer_type): #or ("Pattern Recognition" in summarizer_type and ((i+1)%2==0 or i == len(data_list[j])-1)):
                    continue
                
                #print(i)
                prev_letter = data_list[j][i-1]
                curr_letter = data_list[j][i]
                
                if "Pattern Recognition" in summarizer_type:
                    #print(data_list,j,i)
                    prev_letter = data_list[j][i][0]
                    curr_letter = data_list[j][i][1]  
                
                #print(prev_letter,curr_letter)
                goal_list, conclusion_list = compare_SAX(attr_list[j],prev_letter,curr_letter,summarizer_type,letter_map_list[j])   
                conclusion = conclusion_list[0]
                if "Pattern Recognition" in summarizer_type:
                    summarizer_map = { "better" : "rose",
                                       "about the same" : "stayed the same",
                                       "not do as well" : "dropped"}
                    conclusion = summarizer_map[conclusion_list[0]]                
                        
                #print(prev_letter,curr_letter,conclusion,summarizer)
                if conclusion == summarizer:
                    t_k.append(1)
                else:
                    t_k.append(0)
            elif flag == "compareHR":
                #if i%7 != 0 or i < 7:
                    #continue
                
                #curr_tw = data_list[j][i:i+7]
                #last_tw = data_list[j][i-7:i]
                if "Pattern Recognition" in summarizer_type:
                    last_tw = [data_list[j][i][0]]
                    curr_tw = [data_list[j][i][1]]
                else:
                    curr_tw = [data_list[j][i]]
                    last_tw = [data_list[j][i-1]]               
                #print(curr_tw,last_tw,flag)
                summary, conclusion, goal_list = comparison_TW_SAX_summary(summarizer_type,attr_list,last_tw,curr_tw,"weeks",letter_map_list,i-1,i,flag="eval")
                #conclusion = compare_HR_TW(last_tw,curr_tw,age,activity_level)
                conclusion_map = { 'lower' : 'dropped',
                                   'higher' : 'rose',
                                   'about the same' : 'stayed the same'}
                
                #print(conclusion,summarizers)
                #print(conclusion_map[conclusion[j]],summarizers[j])
                if conclusion_map[conclusion[j]] == summarizer:
                    t_k.append(1)
                else:
                    t_k.append(0)  
            elif flag == "compareACT":
                if i==0:
                    continue
                conclusion, pair_word = compareACT(data_list[j][i-1],data_list[j][i])
                
                if summarizer == conclusion:
                    t_k.append(1)
                else:
                    t_k.append(0)        
            elif flag == "HR" or (attr_list[j] == "Heart Rate" and "Trends" not in summarizer_type):
                #print(hr_evaluation(data_list[j][i],age,activity_level),summarizer)
                if hr_evaluation(data_list[j][i],age,activity_level) == summarizer:
                    t_k.append(1)
                else:
                    t_k.append(0)
            else:
                curr_data = data_list[j][i]
                if "If-then pattern" in summarizer_type:
                    start_index = 1
                    skip_index = 1
            
                    valid = True
                    extra = len(summarizer)
                    for k in range(start_index,len(summarizer)):
                        if i+k >= len(data_list[j]):
                            valid = False
                            break
                        
                        #print(flag,summarizer,k,weekday_map)
                        if flag != None and summarizer[k] in weekday_map.keys():
                            #input(weekday_map.keys())
                            curr_data += str(weekday_map[flag[i+k]])
                        else:
                            curr_data += data_list[j][i+k]
                    if not valid or len(summarizer)==0:
                        continue
                goal = None
                if goals != None and None not in goals:
                    try:
                        goal = goals[j][i]     
                    except IndexError:
                        #goal = goals[j]
                        try:
                            goal = goals[j]
                        except IndexError:
                            goals = goals[0]
                            try:
                                goal = goals[j][i]
                            except IndexError:
                                goal = goals[j]           
                
                #print(curr_data)
                #print(summarizer_type)
                #print(summarizer_type,summarizer,flag,goal,curr_data)
                #input(get_muS(attr_list[j],summarizer_type,summarizer,curr_data,letter_map_list[j],alpha_sizes[j],flag=flag,goal_=goal))
                if get_muS(attr_list[j],summarizer_type,summarizer,curr_data,letter_map_list[j],alpha_sizes[j],flag=flag,goal_=goal):
                    t_k.append(1)
                else:
                    t_k.append(0)
        #print(sum(t_k),len(t_k))
        if sum(t_k)==0:
            r_k = 1
        else:
            r_k = sum(t_k)/float(len(t_k))
        #print(len(t_k),len(data_list[0]), t_k)
        r_list.append(r_k)
        
    #print(r_list,t3)

    r = 1
    for i in range(len(r_list)):
        r *= r_list[i]
        
    #print(r,t3)
            
    return abs(r - t3)

def degree_of_imprecision(avg_list):
    avg_product = 1
    for i in range(len(avg_list)):
        avg_product *= avg_list[i]
        
    m = len(avg_list)
    root = avg_product ** (1.0/m)
    
    imprecision = 1 - root
    #input(imprecision)
    return imprecision

def degree_of_informativeness(alpha,n,truth,quantifier,summs,r_list,summarizers):
    q_list = ["all of the","most of the","more than half of the", "half of the","some of the","almost none of the","none of the"]
    neg_truth = 1 - truth

    quant_index = q_list.index(quantifier)
    quantifier_c = q_list[(-1*quant_index)-1]
    
    #print(quantifier,quantifier_c)
    
    card_q = 0.0
    card_qc = 0.0
    
    for r in r_list:
        muQ = get_muQ(quantifier,r)
        muQc = get_muQ(quantifier_c,r)
        
        if muQ >= alpha:
            card_q += 1
        if muQc >= alpha:
            card_qc += 1

    if not card_q:
        sp_q = 0
    else:
        sp_q = 1.0/card_q
    if not card_qc:
        sp_qc = 0
    else:
        sp_qc = 1.0/card_qc
        
    #input([sp_q,sp_qc])
        
    s = summs[0]
    summ_index = summarizers[0].index(s)
    neg_summ_index = (-1*summ_index)-1
    s_c = summarizers[0][neg_summ_index]
    
    card_s = r_list[summ_index]*n
    card_sc = r_list[neg_summ_index]*n
    
    if not card_s:
        sp_s = 0
    else:
        sp_s = 1.0/card_s
    if not card_sc:
        sp_sc = 0
    else:
        sp_sc = 1.0/card_sc    
    
    #print(truth,sp_q,sp_s)
    measure = truth*sp_q*sp_s
    measure_c = neg_truth*sp_qc*sp_sc
    
    #input([measure,measure_c])
    #s_c = []
    #for i in range(len(summs)):
        #s = summs[i]
        #summ_index = summarizers[i].index(s)
        #s_c.append(summarizers[i][(-1*summ_index)-1])     
    input(s_c)
def get_summary_length(num_summarizers):
    """
    Inputs: 
    - summary: the summary
    
    Outputs: the summary length
    
    Purpose: to calculate the fifth truth value T5. This helps avoid long summaries that are not easily comprehensible by the human user
    """     
    return 2 * (0.5 ** num_summarizers)
        
def get_simplicity(value): 
    """
    Inputs: 
    - value: total number of qualifiers and summarizers
    
    Outputs: the simplicity
    
    Purpose: to calculate the simplicity of the summary.
    """     
    return 2 ** (2 - value)    
    

####### DATA FUNCTIONS #######

def get_data_list(index_list,dataset,demo=False,constraints=False):
    '''
    Inputs:
    - index_list: list of indices of files to be used in the corresponding 
    data folder
    - dataset: the dataset to be used
    
    Outputs list of dataframes
    
    Purpose: Sets up data for the system
    '''
    
    index = 'date'
    
    # Sets up search for specific csv files in data folder
    if dataset == "Stock Market Data":
        data_folder = "data/Stock Market Data"
        #columns_ = ['date','Volume','Close Value','High','Open','Low']
        columns_ = ['date','AAPL close value','AET close value']
        column_list = columns_
        #column_list = ['date','close value']
    elif dataset in ["Heart Rate","Step Count","ActivFit"]:
        data_folder = "data/Insight4Wear"
        columns_ = ['date','Heart Rate','Step Counts']
        if dataset == "Step Count":
            column_list = ["date","Step Counts"]
        elif dataset == "Heart Rate":
            column_list = ["date","Heart Rate"]
        elif dataset == "ActivFit":
            columns_ = ["date","ActivFit"] # TODO: Extend this to be times of day
            column_list = columns_
    elif dataset == "Calorie Intake":
        data_folder = "data/Food Data"
        columns_ = ["date","Calorie Intake"]
        column_list = ["date","Calorie Intake"]
    elif dataset == "Weather":
        data_folder = "data/Weather"
        #columns_ = ["YEARMODA","Alabama temperature","Alaska temperature"]
        columns_ = ["DATE","Average Temperature","TMAX","TMIN","Average Wind Speed","PRCP","SNOW","SNWD","WDF2","WDF5","WSF2","WSF5"]
        column_list = ["DATE","Average Temperature","Average Wind Speed"]
        #index = 'YEARMODA'
        index = "DATE"
    elif dataset == "WeatherHourly":
        data_folder = "data/Weather"
        columns_ = ["DATE","HLY-DEWP-10PCTL","HLY-DEWP-90PCTL","HLY-DEWP-NORMAL","HLY-HIDX-NORMAL","HLY-TEMP-10PCTL","HLY-TEMP-90PCTL","Average Temperature","HLY-WCHL-NORMAL","HLY-WIND-1STDIR","HLY-WIND-1STPCT","HLY-WIND-2NDDIR","HLY-WIND-2NDPCT","Average Wind Speed","HLY-WIND-PCTCLM","HLY-WIND-VCTDIR","HLY-WIND-VCTSPD"]
        column_list = ["DATE","Average Temperature","Average Wind Speed"]
        index = "DATE"    
    elif dataset == "MyFitnessPal":
        if demo:
            #data_folder = "data/MyFitnessPal/DemoData/DemoFoodLogs"
            data_folder = "data/MyFitnessPal/DemoData/DemoMeals"
            columns_ = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar"]
        elif constraints:
            #data_folder = "data/MyFitnessPal/FoodLogs"
            #columns_ = ["date","Calories","Carbs","Fat","Protein","Sodium","Sugar","Food"] 
            #column_list = ["date","Calories","Carbs","Fat","Protein","Sodium","Sugar","Food"]     
            data_folder = "data/MyFitnessPal/DemoData/DemoMeals"
            columns_ = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]            
        else:
            data_folder = "data/MyFitnessPal/all_users"
            #data_folder = "data/MyFitnessPal/FoodLogs"
            
            columns_ = ["date","Calories","Carbohydrates","Fat","Protein","Sodium","Sugar","Food"]    
            column_list = ["date","Calories","Carbohydrates","Fat","Protein","Sodium","Sugar"]
        #raw_input(index_list)
    elif dataset == "MyFitnessPalMeals":
        if demo:
            data_folder = "data/MyFitnessPal/DemoData/DemoMeals"
            columns_ = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar"]
            #else:
                #columns_ = ["date","Meal","Calories","Fat","Saturated Fat","Polyunsaturated Fat","Monounsaturated Fat","Trans Fat","Cholesterol","Sodium","Potassium","Carbohydrates","Fiber","Sugar","Protein","Vitamin A","Vitamin C","Calcium","Iron","Note"]  
                #column_list = ["date","Meal","Calories","Carbohydrates","Fat","Polyunsaturated Fat","Monounsaturated Fat","Protein","Sodium","Sugar"]                    
        else:
            data_folder = "data/MyFitnessPal/Meals"
            
            columns_ = ["date","Meal","Calories","Fat","Saturated Fat","Polyunsaturated Fat","Monounsaturated Fat","Trans Fat","Cholesterol","Sodium","Potassium","Carbohydrates","Fiber","Sugar","Protein","Vitamin A","Vitamin C","Calcium","Iron","Note"]  
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Polyunsaturated Fat","Monounsaturated Fat","Protein","Sodium","Sugar"]    
    elif dataset == "StepUp" or dataset == "StepUpPhases":
        data_folder = "data/StepUp"
        columns_ = ["date","Start Date","End Date","Step Count","Treatment","Baseline","Notification","Intervention","Followup","Phase"]    
        column_list = ["date","Start Date","End Date","Step Count","Treatment","Baseline","Notification","Intervention","Followup","Phase"]          
    elif dataset == "StepUpTrimmed":
        data_folder = "data/StepUpTrimmed"
        columns_ = ["date","Start Date","End Date","Step Counts","Treatment","Baseline","Notification","Intervention","Followup","Phase"]    
        column_list = ["date","Start Date","End Date","Step Counts","Treatment","Baseline","Notification","Intervention","Followup","Phase"]   
    elif dataset == "Cue":
        data_folder = "data/StepUpCue"
        columns_ = ["date","Start Date","End Date","Habit","Habit Time","Treatment"]
        column_list = ["date","Start Date","End Date","Habit","Habit Time","Treatment"]
    elif dataset == "Arm Comparison":
        #data_folder = "data/StepUpArms"
        #columns_ = ["Participant","Attribute","Protoform Type","Quantifier (Goal)","Summarizer (Goal)","Quantifier (Cue)","Summarizer (Cue)"]
        #column_list = ["Participant","Attribute","Protoform Type","Quantifier (Goal)","Summarizer (Goal)"] 
        #data_folder = "data/ArmsStepUp/clusters/A3"
        data_folder = "data/ArmsMFP"
        columns_ = ["Participant","Attribute","Time Window","Protoform Type","Quantifier","Summarizer","Qualifier"]
        column_list = ["Participant","Attribute","Time Window","Protoform Type","Quantifier","Summarizer","Qualifier"]            
        index = "Participant"
    elif dataset == "Energy Deficit":
        if demo:
            data_folder = "data/MyFitnessPal/DemoData/DemoMeals"
            columns_ = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar"]
        else:
            data_folder = "data/MyFitnessPal/EnergyDeficit"      
        
            columns_ = ["date","Calories Consumed","Calories Burned","Energy Deficit"]
            column_list = ["date","Energy Deficit"]
    elif dataset == "SatFatDecrease":
        if demo:
            data_folder = "data/MyFitnessPal/DemoData/DemoMeals"
            columns_ = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar","Food","url","id","Ingredients"]
            column_list = ["date","Meal","Calories","Carbohydrates","Fat","Saturated Fat","Protein","Sodium","Sugar"]
            #index = "Date"            
        else:
            data_folder = "data/MyFitnessPal/Meals"
            
            columns_ = ["date","Meal","Calories","Fat","Saturated Fat","Polyunsaturated Fat","Monounsaturated Fat","Trans Fat","Cholesterol","Sodium","Potassium","Carbohydrates","Fiber","Sugar","Protein","Vitamin A","Vitamin C","Calcium","Iron","Note"]
            column_list = ["date","Saturated Fat"]    
    elif dataset == "FoodPreferences":
        if demo:
            data_folder = "data/MyFitnessPal/DemoData/DemoFoodLogs"
        else:
            data_folder = "data/MyFitnessPal/FoodLogs"
            
        columns_ = ["date","Calories","Carbohydrates","Fat","Protein","Sodium","Sugar","Food","Ingredients"]    
        column_list = ["date","Ingredients"]    
        
    csv_list = os.listdir(data_folder)
    csv_list = [x for x in csv_list if ".csv" in x and "AO" not in x]
    
    days = []
    df_lists = []
    #print(dataset)
    if dataset == "MyFitnessPal" or dataset == "Stock Market Data" or dataset == "StepUp":
        pid_list = []
    else:
        pid_list = None
    #avg_length = 0
    for i in range(len(index_list)):
        df_list = dict()
        data_index = index_list[i]
        #print(data_index, dataset, csv_list, demo)
        #print(data_folder)
        #input(csv_list[data_index])
        #input([len(csv_list),len(index_list)])
        #input(csv_list)
        #print(data_index,csv_list)
        #input(len(csv_list))
        file_name = csv_list[data_index]
        #print(file_name)
        #input(csv_list)        
        df = pd.read_csv(data_folder + "/" + csv_list[data_index],usecols=column_list)
        #input(df)
        if dataset == "Stock Market Data":
            stock_name = file_name.strip(".csv")
            pid_list.append(stock_name)
            
        if dataset == "MyFitnessPal":
            if not demo and "log" not in csv_list[data_index]:
                continue
            elif ".[y" in csv_list[data_index]:
                continue
            pid = csv_list[data_index].split('_')
            if len(pid) > 1:
                pid = pid[1]
            elif type(pid) is list and len(pid) == 1:
                pid = pid[0]
            else:
                input(pid)
                
            pid = pid.strip('.csv')
            pid_list.append(pid)            
                
        if dataset == "StepUp":
            pid = file_name.split("_")[2]
            pid_list.append(pid)
        if dataset != "ActivFit" and dataset != "Step Count":
            df.set_index(index)
        #input(df.columns)
        #df.columns = column_list
        #input(df)
        values = []
        #input([column_list,dataset])
        for column in column_list:
            if dataset != "ActivFit" or (dataset == "ActivFit" and column != "ActivFit"):
                values = df[column].tolist()
            else:
                days = df[index]
            #print(column)
            if column == dataset or column == "calorie" or column == "date" or (dataset == "Step Count" and column == "Step Counts"):
                
                # Take out empty data points in data
                if dataset == "Heart Rate":
                    if column == "Heart Rate":
                        values = [x for x in values if not math.isnan(x)]
                    else:
                        hr_vals = df["Heart Rate"].tolist()
                        values = [values[i] for i in range(len(hr_vals)) if not math.isnan(hr_vals[i])]
                elif dataset == "Step Count":
                    values = values[124:362]
                    values.pop(101)
                    #input(values)
                    #input(column)
                elif dataset == "ActivFit":
                    if column == "date":
                        values = df[column].tolist()
                    else:
                        values = df
                else:
                    values = df[column].tolist()
    
            #input([dataset,data_index,column])
            #if dataset == "MyFitnessPal" and data_index == 4 and column == "Fat":
                #input(df_list["Calories"])
                #values = [x*0.4 for x in df_list["Calories"]]
            #elif dataset == "MyFitnessPal" and data_index == 4:
                #values = [x for x in values ]
                
                #for x in df_list["Calories"]:
                    #input(x)
            #input(values)
            #if dataset == "Stock Market Data" and column != "date":
                #column = stock_name + " " + column
            df_list[column] = values
            #print(column)
            #input(values)
            #input(values)
            #if column == 'date':
                #print(values)
        #input(values)/\
        #input(df_list)
        if dataset == "Cue" or dataset == "StepUp" or dataset == "StepUpTrimmed":
            df_list["Filename"] = csv_list[data_index]
            filename = csv_list[data_index].split("_")
            if "cluster" in filename:
                continue
            id_ = filename[2]
            df_list["id"] = id_
        if dataset == "Arm Comparison":
            #df_list["Filename"] = csv_list[data_index]
            filename = csv_list[data_index].split("_")
            if type(filename) is list and len(filename) > 2:
                group = filename[2].split(".")
                if filename[0] == "all":
                    df_list["group"] = group[0]   
                elif filename[1] == "cluster":
                    df_list["group"] = "cluster " + group[0]
            else:
                df_list["group"] = None
        if dataset == "MyFitnessPal" and not demo and not constraints:  
            key_list = sorted(list(df_list.keys()))
            #input(df_list)
            #input(df_list['Carbohydrates'])
            
            for key in key_list:
                
                #if key == "date":
                    #df_list[key] = [item for item in df_list[key] if isinstance(item,str)]
                    ##print(key)
                    ##input(df_list)
                    #continue
                #print(key,df_list[key])
                #input([key,df_list[key],df_list['Carbohydrates']])
                
                if len(df_list[key])==0 or (key != "Date" and isinstance(df_list[key][0],str)):
                    continue
                
                
                #input(df_list['Carbohydrates'])
                vals = []
                goals = []                
                
                val = 0
                first = True
                #print(key_list,len(dataframe))
                #input(dataframe)
                
                from datetime import timedelta
                #input(df_list)
                #for key_ in df_list.keys():
                    #df_list[key_] = [x for x in df_list[key_] if type(x)==str]
                #input(df_list[key])
                dataframe = df_list[key]
                curr_date = datetime.datetime.strptime(df_list["date"][0],"%Y-%m-%d")
                #input(len(dataframe))
                #cnt = 0
                for j in range(len(dataframe)):
                    cnt = len(vals)
                    item = str(dataframe[j])
                    
                    try:
                        item = float(item)
                        date = df_list["date"][j]
                        #input([date,datetime.datetime.strftime(curr_date,"%m/%d/%Y").lstrip("0")])
                        if (date != '{d.month}/{d.day}/{d.year}'.format(d=curr_date) and not first) or (date == '{d.month}/{d.day}/{d.year}'.format(d=curr_date) and j == len(dataframe)-1):
                            #if j == len(dataframe)-1:
                                #val += item
                            val = round(val,1)
                            vals.append(val)
                            val = 0
                            curr_date = datetime.datetime.strptime(date,"%Y-%m-%d")
                        elif first:
                            first = False
                        
                        #if key == "Carbohydrates":
                            #input([date,item,val])
                        val += item
                        
                        #print("val:",val)
                        
                    except ValueError:
                        #vals.append(item)
                    
                    #vals.append(item)
                    #try:
                        item = item.replace('[','').replace(']','')
                        item = item.split(',')
                        try:
                            item = int(item[0].strip())
                            vals.append(item)
                        except ValueError:
                            item = item[0]
                            vals.append(item)
                        #print(item)
                        #item[1] = int(item[1].strip())
                        #vals.append(item[0])
                        #input(vals)
                    except AttributeError:
                        input("a")
                        continue
                    except ValueError:
                        input("v")
                        continue
                    #except:
                        #input(sys.exc_info()[0])
                    
                    #if cnt == len(vals):
                        #input([cnt,vals,dataframe[j],key])
                    #print(j,dataframe[j],len(vals),vals)
                    
                    #print(key,len(vals))
                    #print(vals)
                #input([len(dataframe),len(df_list[key])])
                vals.append(val)
                #input(vals[-1])
                if data_index == -1 and demo and key == "Fat":
                    #input(df_list["Calories"])
                    vals = [x*0.1 for x in vals]
                #if key == "Date":
                    #vals = sorted(list(set(vals)))
                #if key == "Calories":
                    #input(df_list["Calories"][-1])
                    #input(vals[-1])
                df_list[key] = vals
                #print(df_list["Fat"])
                #input(df_list["Calories"])
            #print(set(df_list["Date"]))
            #input(df_list)
            #input(df_list["Calories"][-1])
            df_list["date"] = list(set(df_list["date"]))
            df_list["date"].sort(key = lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
            #input(df_list)  
            #key = "Fat"
            #fig, ax = plt.subplots()
            #plt.xlabel("Days")
            
            #y_map = {"Calories" : "Calorie Intake (in calories)",
                     #"Carbohydrates" : "Carbohydrate Intake (in grams (g))",
                     #"Fat" : "Fat Intake (in grams (g))",
                     #"Sodium" : "Sodium Intake (in milligrams (mg))",
                     #"Protein" : "Protein Intake (in grams (g))",
                     #"Sugar" : "Sugar Intake (in grams (g))"}
            
            #title_map = {"Calories" : "Calorie",
                     #"Carbohydrates" : "Carbohydrate",
                     #"Fat" : "Fat",
                     #"Sodium" : "Sodium",
                     #"Protein" : "Protein",
                     #"Sugar" : "Sugar"}
            #plt.ylabel(y_map[key])
            #plt.plot(df_list[key],linestyle='-',label=key) 
            
            #key = "Calories"
            #plt.ylabel(y_map[key])
            #plt.title("Calorie Intake Data")
            #plt.plot(df_list[key],linestyle='-',label=key)             
            
                #ax.axhline(10000,color='r')
                #plt.plot(df_list[key],linestyle='-',label=key)            

            #plt.legend()
        
   
        if dataset == "ActivFit":
            # Get dates of activity data readings
            ticks = []
            curr_date = None
            values = df[column]
            for i in range(len(days)):
                date = datetime.datetime.strptime(days[i],"%Y-%m-%d %H:%M:%S")
                date_str = str(date.month) + "/" + str(date.day) + "/" + str(date.year)
                if date_str != curr_date:
                    curr_date = date_str
                    ticks.append(i)
        
        #if dataset == "MyFitnessPal":
            #fig, ax = plt.subplots()
            #plt.xlabel("Days")
            #plt.ylabel("Carbohydrate Intake (in grams)")
            ##plt.title("Fat Intake Data")     
            ###ax.axhline(10000,color='r')
            #plt.plot(df_list['Carbohydrates'],linestyle='-')        
            #if i==0 and (dataset == "Step Counts" or dataset == "StepUp"):
                ## Present chart of first individual's data for step counts
                #fig, ax = plt.subplots()
                #plt.xlabel("Days")
                #plt.ylabel("Step Count")
                #plt.title("Step Count Data Snippet")     
                
                #data = []
                #input(df_list["id"])
                #for j in range(len(df_list["Step Counts"])):
                    #pass
                ##ax.axhline(10000,color='r')
                #plt.plot(df_list["Step Counts"],linestyle='-')
                #input(df_list["Step Counts"])
            
        #if i==0 and dataset == "ActivFit":
            ## Present chart for activity data
            #plt.xticks(ticks,[x for x in range(len(ticks))])
            #plt.plot(values,linestyle='-')
            #plt.xlabel("Days")
            #plt.ylabel("Activity")
        #input(df_list.keys())
        #if "Average Temperature" in df_list.keys():
            #fig, ax = plt.subplots()
            #plt.xlabel("Hours")
            #plt.ylabel("Average Wind Speed (in mph)")
            ##plt.title("Fat Intake Data")     
            ###ax.axhline(10000,color='r')
            #plt.plot(df_list['Average Wind Speed'],linestyle='-')            
            ##plt.plot(df_list['AET close value'],linestyle='-')            
        if "Step Counts" in df_list.keys():
            
            data = df_list["Step Counts"]
            
            df_list.pop("Step Counts")
            
            if dataset == "StepUp" or dataset == "StepUpTrimmed":
                #input(df_list["date"])
                new_data = []
                new_dates = []
                #input(df_list["date"][0])
                curr_day = df_list["date"][0]
                curr_day = curr_day.split(" ")[0].split('-')
                curr_day = datetime.date(int(curr_day[0]),int(curr_day[1]),int(curr_day[2]))
                steps = 0
                #curr_day = datetime.datetime(
                for j in range(len(data)):
                    candidate = df_list["date"][j]
                    candidate = candidate.split(" ")[0].split('-')
                    candidate = datetime.date(int(candidate[0]),int(candidate[1]),int(candidate[2]))
                    
                    if candidate == curr_day:
                        #input(steps)
                        steps += data[j]
                    else:
                        new_data.append(steps)
                        new_dates.append(curr_day)
                        steps = data[j]
                        curr_day = candidate
                
                new_data.append(steps)
                new_dates.append(curr_day)                    
                        
                data = new_data       
                df_list["date"] = new_dates
                
                #input(new_data)
                
            df_list["Step Count"] = data
            #input(data)
        if dataset == "MyFitnessPalMeals" or dataset == "MyFitnessPal" or dataset == "SatFatDecrease":
            if "Date" in df_list.keys():
                df_list["date"] = df_list["Date"]
                df_list.pop("Date")
            if "meal" in df_list.keys():
                df_list["Meal"] = df_list["meal"]
                df_list.pop("meal")            
        df_lists.append(df_list)
        #avg_length += len(df_list["Step Count"])
        
    #input(avg_length/len(index_list))
    #input(df_lists[0]["Carbohydrates"])
    #if dataset == "MyFitnessPal":
        #print(dataset)
        #input(df_lists)

    if (constraints or demo) and (dataset == "MyFitnessPalMeals" or dataset == "Energy Deficit" or dataset == "MyFitnessPal" or dataset == "SatFatDecrease"):
        for j in range(len(df_lists)):
            tmp = dict()
            total_list = []
            cnt = {'Calories': 0, 'Carbohydrates': 0, 'Fat' : 0, 'Protein' : 0, 'Saturated Fat' : 0}
            first = True
            sub_set = set([])
            meal_set = set(["Breakfast","Lunch","Dinner","Snacks"])
            prev_date = None
            #input(df_lists[j]["date"])
            for i in range(len(df_lists[j]["date"])):
                date = df_lists[j]["date"][i]
                meal = df_lists[j]["Meal"][i].capitalize()
                #print(date,meal)

                if meal == "Dinner-party":
                    meal = "Dinner"
                if data_index == -1 and demo:
                    carbs = 30
                else:
                    carbs = df_lists[j]["Carbohydrates"][i]
                calories = df_lists[j]["Calories"][i]
                fats = df_lists[j]["Fat"][i]
                protein = df_lists[j]["Protein"][i]
                #input(df_lists[j].keys())
                satfats = df_lists[j]["Saturated Fat"][i]
                
                if prev_date == None:
                    tmp[date] = dict()
                    prev_date = date
                    
                #print(date,prev_date,carbs,calories)
                
                if date != prev_date and prev_date != None:
                    total_list.append(cnt)
                    
                    missing = list(meal_set - sub_set)
                    
                    #input([tmp[prev_date],missing]) 
                    for k in range(len(missing)):
                        null_meal = missing[k]
                        
                        if data_index == -1 and demo:
                            tmp[prev_date][null_meal] = 30
                        else:
                            tmp[prev_date][null_meal] = dict()
                            tmp[prev_date][null_meal]["Calories"] = 0
                            tmp[prev_date][null_meal]["Carbohydrates"] = 0                            
                            tmp[prev_date][null_meal]["Fat"] = 0    
                            tmp[prev_date][null_meal]["Protein"] = 0                                
                            tmp[prev_date][null_meal]["Saturated Fat"] = 0                            
                            #tmp[prev_date][null_meal] = 0
                        
                    #input(tmp[prev_date])
                    sub_set = set([])       
                    tmp[date] = dict()
                    prev_date = date         
                    cnt = {'Calories': 0, 'Carbohydrates': 0, 'Fat' : 0, 'Protein' : 0, 'Saturated Fat' : 0}
                               
                tmp[date][meal] = dict()
                tmp[date][meal]["Calories"] = calories
                tmp[date][meal]["Carbohydrates"] = carbs
                tmp[date][meal]["Fats"] = fats
                tmp[date][meal]["Protein"] = protein
                tmp[date][meal]["Saturated Fats"] = fats
                                
                #input(tmp)
                    
                #first = False
                #cnt += carbs
                cnt['Carbohydrates'] += carbs
                cnt['Calories'] += calories
                cnt['Fat'] += fats
                cnt['Protein'] += protein
                #input(cnt.keys())
                cnt['Saturated Fat'] += fats
                sub_set.add(meal)
              
            total_list.append(cnt)
            
            
            missing = list(meal_set - sub_set)
            #input([tmp[prev_date],missing])
            for i in range(len(missing)):
                null_meal = missing[i]
                tmp[prev_date][null_meal] = dict()
                tmp[prev_date][null_meal]["Calories"] = 0
                tmp[prev_date][null_meal]["Carbohydrates"] = 0           
                tmp[prev_date][null_meal]["Fat"] = 0           
                tmp[prev_date][null_meal]["Protein"] = 0           
                tmp[prev_date][null_meal]["Saturated Fats"] = 0           
            #tmp["Total"] = total_list
            #for key in tmp.keys():
                #print(key, tmp[key])
                #print()
            #input()
            final_dict = dict()
            dates = []
            for key in tmp:
                dates.append(key)
                for subkey in tmp[key]:
                    if subkey not in final_dict.keys():
                        final_dict[subkey] = [tmp[key][subkey]]
                    else:
                        final_dict[subkey].append(tmp[key][subkey])
            final_dict["Total"] = total_list
            final_dict["date"] = dates
            
            if demo:
                df_lists[j] = [final_dict]
            elif constraints:
                meal_set = set(df_lists[j]["Meal"])
                meal_set.add("Total")
                for meal in meal_set:
                    df_lists[j][meal] = final_dict[meal]
                #for meal.capitalize() in df_lists[j]["Meal"]:
                    
        
    
        
    #input(df_lists)
    #print(os.getcwd())
    
    #with open("data/MyFitnessPal/FoodLogs/ACM/weather_hourly_data.csv","w",newline='') as file_var:
        #import csv
        #csvwriter = csv.writer(file_var, delimiter=',')
        #csvwriter.writerow(["Day","Average Temperature","Average Wind Speed"])
        #data_list = df_lists[0]["Average Temperature"]
        #data_list2 = df_lists[0]["Average Wind Speed"]
        #day_list = list(range(1,len(data_list)+1))
        ##input(day_list)
        #for i in range(len(data_list)):
            #csvwriter.writerow([day_list[i],data_list[i],data_list2[i]])
    ##data_file.write("Calories")
    ##data_list = df_lists[0]["Calories"]
  
    ##data_file.close()
    #input()
    #print(df_list)
    return df_lists, pid_list

def create_database(sax_list,num_sax,letter_map_list,tw,alpha_sizes,prefix,weekdays=None):
    '''
    Inputs:
    - sax_list: list of SAX representations of data 
    - num_sax: number of variables
    - weekdays: list of weekdays corresponding to SAX symbols
    - letter_map: a mapping from letters to integers
    - tw: the time window (default is "the past week")
    - alpha_size: the alphabet size
    - prefix: prefix for file name
    
    Outputs: Total number of sequences
    
    Purpose: Creates input data file to be read for cSPDADE
    '''
    db_filename = prefix + ".ascii"
    data_file = open(db_filename,"w")

    seq_id = 1
    evt_id = 1
    
    weekday_map = {"Monday" : 1,
                     "Tuesday" : 2,
                     "Wednesday" : 3,
                     "Thursday" : 4,
                     "Friday" : 5,
                     "Saturday" : 6,
                     "Sunday" : 7}
    
    weekday_list = []
    if weekdays != None:
        for day in weekdays:
            weekday_list.append(weekday_map[day])
    else:
        weekday_list = ['']*len(sax_list[0])
        
    index = 0
    for i in range(0,len(sax_list[0]),tw):
        
        substring = sax_list[0][i:i+tw]
            
        for j in range(0,len(substring)):
            item_str = ""
            for k in range(len(sax_list)):
                substr = sax_list[k][i:i+tw]
                #print(weekday_list,index,letter_map_list,k,substr[j],alpha_sizes)
                item = str(weekday_list[index]) + str(letter_map_list[k][substr[j]] + alpha_sizes[k]*k)

                item_str += item + " "
            index += 1
            item_str.strip(" ")
            line = str(seq_id) + " " + str(j+1) + " " + str(num_sax) + " " + item_str + '\n'
            
          
            ascii = line.encode('ascii')
            data_file.write(line)
            evt_id += 1
        seq_id += 1
    
    data_file.close()
    return seq_id-1

####### PATTERN FUNCTIONS #######

def parse_patterns(content,var="uni"):
    '''
    Inputs:
    - content: the patterns to be parsed
    
    Outputs:
    - parsed_content: parsed patterns
    
    Purpose: parses patterns returned by the SPADE algorithm
    '''
    supports = []
    # Parse patterns
    for i in range(len(content)):
        content[i] = content[i].strip('\n')
        content[i] = content[i].split(' -- ')
        
        supports.append(int(content[i][-1].strip()))
        
        content[i] = content[i][:-1]
        content[i] = content[i][0].split(' -> ')
    
    # Remove 1-sequences
    parsed_content = []
    final_supports = []
    for i in range(len(content)):
        if len(content[i]) > 1:
            parsed_content.append(content[i])
            final_supports.append(supports[i])
    
    supports = final_supports
    # If multivariate, remove sequences that lead to univariate pattern summaries
    if var == "multi":
        index_list = []
        for i in range(len(parsed_content)):
            
            space_cnt = 0
            for j in range(len(parsed_content[i])):
                space_cnt += parsed_content[i][j].count(' ')
                
            if space_cnt == 0:
                index_list.append(i)
                                
        for index in sorted(index_list, reverse=True):
            del parsed_content[index]
            del supports[index]
        
    return parsed_content,supports
     
def get_patterns(sax_list,num_sax,letter_map_list,tw,alpha_sizes,prefix,path,cygwin_path,min_sup,weekdays=None):
    '''
    Inputs:
    - sax_list: list of SAX representations of the time series
    - num_sax: number of variables
    - letter_map: a mapping from letters to integers
    - tw: the time window size (default is "the past week")
    - alpha_size: the alphabet size
    - prefix: prefix for file name
    - path: file path used for files needed for SPADE algorithm
    - cygwin_path: file path of Cygwin or other module to run SPADE commands
    - min_sup: minimum support value
    - weekdays: list of weekdays corresponding to SAX symbols
    
    Outputs total number of sequences and the parsed patterns of the content from SPADE
    
    Purpose: To retrieve the patterns SPADE finds in the SAX representation
    '''
    # Create a data file for CSPADE
    num_seqs = create_database(sax_list,num_sax,letter_map_list,tw,alpha_sizes,prefix,weekdays=weekdays)    
    
    # Change to Cygwin path
    os.chdir(cygwin_path)
    
    # Create .data file
    input_file = path + prefix + ".ascii"
    output_file = path + prefix + ".data"
    makebin = [path + "makebin.exe", input_file, output_file]
    subprocess.check_output(makebin,stderr=subprocess.STDOUT)
    
    # Create .conf file
    file_path = path + prefix
    getconf = [path + "getconf.exe", "-i", file_path, "-o", file_path]
    subprocess.check_output(getconf,stderr=subprocess.STDOUT) 
    
    # Create .tpose and .idx files
    #close(file_path + ".idx")
    #input(os.listdir())
    exttpose = [path + "exttpose.exe", "-i", file_path, "-o", file_path, "-l", "-s", "0", "-x"]
    try:
        subprocess.check_output(exttpose,stderr=subprocess.STDOUT) 
    except subprocess.CalledProcessError as e:
        input(e.output)
        return None, None, None
    
    # Get sequences and output them to patterns.txt file
    minimum_support = str(min_sup)
    TW = str(tw)
    os.chdir(path)
    #input(os.listdir())
    os.chdir(cygwin_path)
    #input("spade")
    seq_length = str(len(sax_list)*2)
    spade = [path + "spade.exe", "-e", "1", "-i", file_path, "-s", minimum_support, "-o", "-w", TW, "-u", "1","-Z",seq_length]
    output_file = open(path + "patterns.txt","w")
    subprocess.call(spade,stdout=output_file)
    output_file.close()    
    
    os.chdir(path)
    #input("back to path")
    
    with open("patterns.txt","r") as patterns_file:
        content = patterns_file.readlines()
            
    content = content[2:]
    var_ = "uni"
    if num_sax > 1:
        var_ = "multi"
                        
    content,supports = parse_patterns(content,var=var_)
    return num_seqs, content, supports

def pattern_freq(summarizers,summarizer_map,alphabet,sax_list,letter_map,weekday_dict,tw,alpha_size,weekday_list=None,weekdays=None):
    '''
    Inputs: 
    - summarizers: a list of list of summarizers
    - summarizer_map: a mapping from summarizers to letters
    - sax_list: list of SAX representations of the time series 
    - alphabet: alphabet of letters used for SAX
    - letter_map: a mapping from letters to integers
    - weekday_dict: mapping from numbers to corresponding weekdays
    - tw: the time window (default is "the past week")
    - alpha_size: the alphabet size
    - weekday_list: list of weekdays corresponding to patterns
    - weekdays: list of weekdays corresponding to SAX symbols

    Outputs:
    - freqs: frequencies of each pattern in the SAX representation
    '''    
    import re
    freqs = []

    for i in range(len(summarizers)):
        pattern = summarizers[i]
        sax_pattern = []
        
        for j in range(len(pattern)):
            part = pattern[j]
            sub_pattern = []
            
            for k in range(len(part)):
                attribute = part[k]
                
                sax = ""
                for l in range(len(attribute)):
                    summarizer = attribute[l]
                    sax += summarizer_map[summarizer]
                    
                sub_pattern.append(sax)
                
            sax_pattern.append(sub_pattern)
        
        full_patterns = []
        
        for j in range(len(sax_pattern)):
            
            max_len = 0
            for k in range(len(sax_pattern[j])):
                if len(sax_pattern[j][k]) > max_len:
                    max_len = len(sax_pattern[j][k])
                                        
            for k in range(len(sax_pattern[j])):
                if len(sax_pattern[j][k]) < max_len:
                    sax_pattern[j][k] += " "*(max_len - len(sax_pattern[j][k]))
                    
        if len(sax_list) > 1: 
            
            # Iterate over columns
            sax_matrix = np.matrix(sax_pattern).T
            sax_pattern = sax_matrix.tolist()            
            
            str_list = [""]*len(sax_pattern)
            for j in range(len(sax_pattern)):
                for k in range(len(sax_pattern[j])):
                    str_list[j] += sax_pattern[j][k]
        else:
            str_list = [""]
            for j in range(len(sax_pattern)):
                for k in range(len(sax_pattern[j])):
                    str_list[0] += sax_pattern[j][k]

        index_lists = []
        for j in range(len(str_list)):
            sax_str = str_list[j].replace(' ','.')
            regex = '(?=' + sax_str + ')'
            index_lists.append([x.start() for x in re.finditer(regex,sax_list[j])])
                        
        # Weekday filter
        remove_list = []
        if weekday_list != None:
            for j in range(len(index_lists)):
                for k in range(len(index_lists[j])):
                    index = index_lists[j][k]
                    for l in range(len(weekday_list[i])):
                        if index+l == len(weekdays):
                            remove_list.append(index)
                            break
                        
                        if weekdays[index+l] != weekday_dict[int(weekday_list[i][l])]:
                            remove_list.append(index)
                            break

        index_set = set(index_lists[0]) # TODO: Check if this breaks multi
        
        
        remove_set = set(remove_list)
        index_set = index_set - remove_set
        
        for j in range(1,len(index_lists)):
            index_set = index_set.intersection(set(index_lists[j]))
            
        freqs.append(len(index_set))
        
    return freqs

def reconstruct_pattern(pattern,weekday_list,character='-'):
    '''
    Inputs:
    - pattern: frequent pattern in 'x-x-x-x' format
    - weekday_list: list of corresponding weekdays
    
    Outputs:
    - original: original pattern before separation
    
    Reconstructs pattern string before separation of SAX letters and weekdays in analyze_patterns
    '''
    original = ""  
    
    pattern = pattern[:-1]
    # Placeholder for connection between prefix and suffix
    pattern.insert(1,'')    
    
    orig = ""
    index = 0
    tmp_pattern = pattern
    for item in tmp_pattern:
        if item == '':
            orig += character
            continue
        
        for i in range(len(item)):
            if i==0 or item[i-1] == '-' or item[i-1] == '_':
                orig += weekday_list[index]
                index += 1
                
            orig += item[i]
    
    return orig
                    

def analyze_patterns(attr_list,sax_list,alphabet_list,letter_map_list,weekday_dict,tw,alpha_sizes,prefix,path,cygwin_path,min_conf,min_sup,proto_cnt,flag_=None,weekdays=None,food_items=False):
    '''
    Inputs: 
    - attr_list: a list of summarizers
    - sax_list: list of SAX representations of the time series 
    - alphabet: alphabet of letters used for SAX
    - letter_map: a mapping from letters to integers
    - weekday_dict: mapping from numbers to corresponding weekdays
    - tw: the time window (default is "the past week")
    - alpha_size: the alphabet size
    - prefix: prefix for file name
    - path: file path used for files needed for SPADE algorithm
    - cygwin_path: file path of Cygwin or other module to run SPADE commands
    - min_sup: minimum support value
    - min_conf: minimum confidence threshold    
    - proto_cnt: current number of summaries generated
    - flag_: flag used for unique data (default is None)
    - weekdays: list of weekdays corresponding to SAX symbols

    Outputs:
    - summary_list: list of if-then pattern summaries
    - proto_cnt: new number of summaries generated
    '''
    num_seqs,patterns,supports = get_patterns(sax_list,len(sax_list),letter_map_list,tw,alpha_sizes,prefix,path,cygwin_path,min_sup,weekdays=weekdays)
    
    tmp_list = []
    for i in range(len(attr_list)):
        words = attr_list[i].split(' ')
        word_str = ""
        for j in range(len(words)):
            try:
                word_str += words[j][0].lower() + words[j][1:]
            except IndexError:
                print("analyzepatterns error")
                input([words,j])
            if j != len(words)-1:
                word_str += " "
                
        tmp_list.append(word_str)
            
        if tmp_list[i][-1] == "s":
            tmp_list[i] = tmp_list[i][:-1]  
    
    attr_list = tmp_list
    pattern_dict = dict()
    prefix_cnt = dict()
    
    string_patterns = []
    support_dict = dict()
    for i in range(len(patterns)):
        pattern = patterns[i]
        for j in range(len(pattern)):
            pattern[j] = pattern[j].replace(' ','_')
        str_pattern = '-'.join(pattern)
        support_dict[str_pattern] = supports[i]
        string_patterns.append(str_pattern)
    
    max_len = 0
    #input(string_patterns)
    for pattern in string_patterns:
        if len(pattern) > max_len:
            max_len = len(pattern)
            
    index = 1 
    cnt = -1
        
    while index < max_len-1:
        for item in string_patterns:
            
            # Retrieve possible prefixes and suffixes
            prefix = item[:index].strip()
            suffix = item[index:].strip()
            
            if len(suffix) == 0 or len(prefix) == 0:
                continue            
            
            if prefix == '-' or suffix == '-' or prefix == '_' or suffix == '_':
                continue
            
            if prefix[-1] == '-' or suffix[-1] == '-' or prefix[-1] == '_' or suffix[-1] == '_':
                continue            
            
            if item[:(index+1)][-1] != '_' and item[:(index+1)][-1] != '-':
                continue
            
            prefix = prefix.strip('-').strip('_')
            suffix = suffix.strip('-').strip('_')
            
            # Map prefixes to subsuffixes and corresponding counts
            if prefix not in pattern_dict.keys():
                pattern_dict[prefix] = dict()
              
            # Count prefix occurences
            if prefix not in prefix_cnt.keys():
                prefix_cnt[prefix] = 0           
           
            if suffix not in pattern_dict[prefix].keys():
                pattern_dict[prefix][suffix] = 1
            else:
                pattern_dict[prefix][suffix] += 1
            prefix_cnt[prefix] += 1                   
            
        index += 1
        
    # Compute confidences of prefix-suffix pairs
    freq_patterns = []
    for key in pattern_dict.keys():
        for subkey in pattern_dict[key].keys():
            pattern_dict[key][subkey] = float(pattern_dict[key][subkey])/float(prefix_cnt[key])
            freq_patterns.append([key.strip(),subkey,pattern_dict[key][subkey]])
                    
    
    # Sort frequent pattern candidates by subsuffix counts
    freq_patterns = sorted(freq_patterns,key = lambda x: x[2],reverse=True)
    
    # Remove patterns that do not reach the minimum confidence threshold
    index = 0
    broke = False
    for i in range(len(freq_patterns)):
        if freq_patterns[i][2] <= min_conf:
            index = i
            broke = True
            break
        
    if broke:
        freq_patterns = freq_patterns[:index]   
    
    symbol_dict = dict()
    index = 0
    for p in freq_patterns:
        combo = p[0] + p[1]
        for i in range(len(combo)):
            if combo[i] == "_" or combo[i] == '-':
                symbol_dict[index] = combo[i]
                index += 1
        
    index = 0
    weekday_list = None
    if weekdays != None:
        weekday_list = []
        weekday_origs = []
        #pattern_lengths = []
        #for i in range(len(freq_patterns)):
            #pattern_lengths.append(len(freq_patterns[i][0].split('_')))
            
        #print(freq_patterns)
        for i in range(len(freq_patterns)):
            #sub_list = [[] for i in range(len(attr_list))]
            sub_list = []
            for j in range(len(freq_patterns[i])-1):
                part = freq_patterns[i][j]
                part = part.split('-')
                tmp = []
                for k in range(len(part)):
                    subpart = part[k]
                    #print(i,subpart)
                    
                    if '_' not in subpart:
                        sum_ = 0
                        num = int(subpart[1:])
                        index_ = 0
                        res = []
                        #print(subpart)
                        for l in range(len(alpha_sizes)):
                            sum_ += alpha_sizes[l]
                            #print(num,sum_)
                            if num <= sum_:
                                index_ = l
                                break
                            #print(num,sum_)
                            res.append('')
                        #res = ['' for l in range(index_)]
                        
                        res.append(subpart[0])
                        #print(i,res,index_)
                        length = len(attr_list)-index_
                        
                        #length = 2
                        #print([pattern_lengths[i],index_,length,res])
                        #print(part,length,len(part),index,freq_patterns[i])
                        for l in range(length-1): res.append('')
                        #print(length-1)
                        #print(res)
                        sub_list.append(res)
                    else:
                        subpart_ = subpart.split('_')
                        #print(subpart_)
                        length = min(max([len(x) for x in subpart_]),2)
                        #length = 2
                        
                        res = [x[0] for x in subpart_]
                        
                        import copy
                        n = copy.deepcopy(len(res))
                        #print(res,length,subpart_)
                        for l in range(length-n): res.append('')
                        #print(res,length)
                        sub_list.append(res)
                        #max_length = max([len(x) for x in sub_list])
                        #for l in range(len(sub_list)):
                            #if len(sub_list[l]) < max_length:
                                #diff = max_length - len(sub_list[l])
                                #for r in range(diff): sub_list[l].append('')
                        
                        #print(sub_list,max_length,freq_patterns[i])
                    #print(length)    
                    subpart = subpart.split('_')
                    for l in range(len(subpart)):
                        #sub_list[l].append(subpart[l][0])
                        tmp.append(subpart[l][1:])
                
                tmp_str = ""
                for k in range(len(tmp)):
                    tmp_str += tmp[k]
                    if k != len(tmp)-1:
                        tmp_str += symbol_dict[index]
                        index += 1
                        
                freq_patterns[i][j] = tmp_str
              
            #input(sub_list)
            weekday_list.append(sub_list)
        #input(weekday_list)
        
    #if weekdays != None:
        #print(freq_patterns)
        #input(weekday_list)
    summary_list = []
    result_summarizers = []
    summarizer_map = dict()
    support_list = []
    numsum_list = []
    #input(freq_patterns)
    if food_items: 
        for i in range(len(freq_patterns)):
            pattern_data = freq_patterns[i]
            prefix = pattern_data[0]
            suffix = pattern_data[1]   
            
            pattern = prefix+"-"+suffix
            if pattern in string_patterns:
                string_patterns.remove(pattern)
            else:
                pattern = prefix+"_"+suffix
                
            support = float(support_dict[pattern])/num_seqs
            freq_patterns[i].append(support)
        return freq_patterns
    
    for p in range(len(freq_patterns)):
        pattern_data = freq_patterns[p]
        
        prefix = pattern_data[0]
        suffix = pattern_data[1]
        conf = float(pattern_data[2])
        
        if weekdays != None:
            weekday_orig = []
            for i in range(len(weekday_list[p])):
                for j in range(len(weekday_list[p][i])):
                    if weekday_list[p][i][j] != '':
                        weekday_orig.append(weekday_list[p][i][j])
            weekday_origs.append(weekday_orig)
        
        if weekdays != None:
            pattern = reconstruct_pattern(pattern_data,weekday_orig)
        else:
            pattern = prefix+"-"+suffix
            if pattern in string_patterns:
                string_patterns.remove(pattern)
            else:
                pattern = prefix+"_"+suffix
        try:
            support_list.append(float(support_dict[pattern])/num_seqs)
        except KeyError:   
            if weekdays != None:
                pattern = reconstruct_pattern(pattern_data,weekday_orig,character="_")
            else:
                #pattern = prefix+"_"+suffix
                pattern = prefix+"-"+suffix
            #print([prefix,suffix])
            support_list.append(float(support_dict[pattern])/num_seqs)
            
            
        if weekdays != None:
            #print(freq_patterns[p])
            #print(weekday_list[p])
            tmp = []
            max_length = [len(x) for x in weekday_list[p]]
            max_length = max(max_length)
            
            for j in range(max_length):
                sublist = []
                for i in range(len(weekday_list[p])):
                    #print(len(tmp),i,j,weekday_list[p])
                    #print(weekday_list[p])
                    try:
                        sublist.append(weekday_list[p][i][j])
                    except IndexError:
                        continue
                #print(sublist)
                tmp.append(sublist)
            
            #for j in range(len(tmp)):
                #while tmp[j][0] == '':
                    #tmp[j] = tmp[j][1:]
            
            weekday_list[p] = tmp
                
        # Get letters corresponding to integers in patterns
        letters1 = []
        letters2 = []
        
        for i in range(len(sax_list)):
            letters1.append([])
            letters2.append([])
    
        last_letter = ''
        key_index = 0
        #print([prefix,suffix])
        for i in range(len(prefix)):
            if prefix[i] == ' ' or prefix[i] == '-' or prefix[i] == '_':
                #print(prefix[i])
                if prefix[i] == "_":
                    key_index += 1
                elif prefix[i] == "-":
                    key_index = 0
                #elif prefix[i] == "-":
                
                #print(alpha_sizes,len(alpha_sizes),key_index)
                alpha_size = alpha_sizes[key_index]
                alphabet = alphabet_list[key_index]
                if len(last_letter) > 0:
                    #if weekdays != None:
                        #print(last_letter,alpha_size)
                    num = int(last_letter)
                    if num <= alpha_size:
                        #if weekdays != None:
                            #print(1)
                        letters1[0].append(alphabet[(int(last_letter)-1)])
                    else:
                        #if weekdays != None:
                            #print(2)
                        diff = num - alpha_size
                        while diff > alpha_sizes[key_index]:
                            diff -= alpha_sizes[key_index]                        
                        if num < alpha_size:
                            var_index = 1
                        else:
                            var_index = int(math.ceil(num/alpha_size))
                        #if weekdays != None:
                            #print(var_index-1,alphabet[diff-1])                        
                        letters1[var_index-1].append(alphabet[diff-1])
                    last_letter = ''
                continue
            else:
                last_letter += prefix[i]
        
        if len(last_letter) > 0:
            num = int(last_letter)
            if num <= alpha_sizes[key_index]:
                letters1[0].append(alphabet_list[key_index][(int(last_letter)-1)])
            else:
                diff = num - alpha_sizes[key_index]
                while diff > alpha_sizes[key_index]:
                    diff -= alpha_sizes[key_index]
                    
                if num < alpha_sizes[key_index]:
                    var_index = 1
                else:
                    var_index = int(math.ceil(num/alpha_sizes[key_index]))
                    
                letters1[var_index-1].append(alphabet_list[key_index][diff-1])
            last_letter = ''
        
        #if weekdays != None:
            #print(letters1)
            
        key_index = 0
        for i in range(len(suffix)):
            if suffix[i] == ' ' or suffix[i] == '-' or suffix[i] == '_':
                if suffix[i] == "_":
                    key_index += 1
                #print([alpha_sizes,key_index])
                alpha_size = alpha_sizes[key_index]
                alphabet = alphabet_list[key_index]                
                if len(last_letter) > 0:
                    num = int(last_letter)
                    if num <= alpha_size:
                        letters2[0].append(alphabet[(int(last_letter)-1)])
                    else:
                        diff = num - alpha_sizes[key_index]
                        while diff > alpha_sizes[key_index]:
                            diff -= alpha_sizes[key_index]                        
                        if num < alpha_size:
                            var_index = 1
                        else:
                            var_index = int(math.ceil(num/alpha_size))

                        letters2[var_index-1].append(alphabet_list[key_index][diff-1])
                    last_letter = ''               
                continue
            else:    
                last_letter += suffix[i]

        if len(last_letter) > 0:
            num = int(last_letter)
            if num <= alpha_sizes[key_index]:
                letters2[0].append(alphabet_list[key_index][(int(last_letter)-1)])
            else:
                diff = num - alpha_sizes[key_index]
                while diff > alpha_sizes[key_index]:
                    diff -= alpha_sizes[key_index]                
                if num < alpha_size:
                    var_index = 1
                else:
                    var_index = int(math.ceil(num/alpha_size))
             
                letters2[var_index-1].append(alphabet_list[key_index][diff-1])
            last_letter = ''   
                        
        # Convert letters to summarizers
        summarizers1 = []
        summarizers2 = []
        
        for i in range(len(sax_list)):
            summarizers1.append([])
            summarizers2.append([])   
            
        for i in range(len(letters1)):
            if len(letters1[i]) == 0:
                continue
            for j in range(len(letters1[i])):
                if attr_list[i] == "Heart Rate" or attr_list[i] == "heart rate":
                    flag_ = "HR"
                elif attr_list[i] in ['breakfast', 'lunch', 'dinner', 'total']:
                    flag_ = "CC"
                else:
                    flag_ = None
                                    
                summarizer = evaluateSAX(letters1[i][j],letter_map_list[i],alpha_sizes[i],flag=flag_)
                summarizers1[i].append(summarizer)
                summarizer_map[summarizer] = letters1[i][j]
                    
        for i in range(len(letters2)):
            if len(letters2[i]) == 0:
                continue            
            for j in range(len(letters2[i])):
                if attr_list[i] == "Heart Rate" or attr_list[i] == "heart rate":
                    flag_ = "HR"
                elif attr_list[i] in ['breakfast', 'lunch', 'dinner', 'total']:
                    flag_ = "CC"                
                else:
                    flag_ = None        
                summarizer = evaluateSAX(letters2[i][j],letter_map_list[i],alpha_sizes[i],flag=flag_)                
                summarizers2[i].append(summarizer)
                summarizer_map[summarizer] = letters2[i][j]
            
            
        summarizers1 = [x for x in summarizers1 if x != '-' and x != '_']
        summarizers2 = [x for x in summarizers2 if x != '-' and x != '_']      
        
        
        
        #if weekdays != None:
            #print(summarizers1) 
            #input(summarizers2)
        #else:
            #print(summarizers1) 
            #input(summarizers2)            
        import copy
        result_summarizers.append([copy.deepcopy(summarizers1),copy.deepcopy(summarizers2)])
        
            
        # Construct if-then pattern summary
        first = "There is " + str(int(conf*100)) + "% confidence that, when"
        second = ""
        third = ""
        abort = False
        weekday_index = 0
        num_summarizers = 0
        particle = "your"
        weather_flag = False
        for attr_ in attr_list:
            if "temperature" in attr_ or attr_ == "Average Temperature" or "close value" in attr_:
                weather_flag = True
                break
        
        if weather_flag:
            particle = "the"
            
        #if weekdays != None:
            #print(summarizers1)
            #print(summarizers2)
        #print(summarizers1,summarizers2)
        for i in range(len(summarizers1)):
            if len(summarizers1[i]) == 0:
                continue
            if second != "":
                second += ", and"
                
            attribute_ = attr_list[i]
            if not weather_flag:
                attribute_ = attribute_.lower()
            elif "close value" in attr_:
                tmp = attribute_.split(" ")
                tmp[0] = tmp[0].upper()
                tmp_str = ""
                for j in range(len(tmp)):
                    tmp_str += tmp[j]
                    if j != len(tmp)-1:
                        tmp_str += " "
                attribute_ = tmp_str         
            if attr_list[i] == "breakfast":
                attribute_ = "carbohydrate intake"
            
            second += " " + particle + " " + attribute_ + " follows the pattern of being "
            #if weekdays != None:
                #print(summarizers1,weekday_dict[int(weekday_list[p][weekday_index])])
            for j in range(len(summarizers1[i])):
                if third != "":
                    third += ", then "
                third += summarizers1[i][j] 
                
                if weekdays != None:
                    #print(p,weekday_list,weekday_index
                    #print(summarizers1)
                    #print(weekday_list[p],summarizers1,i,0,freq_patterns[p])
                    #print(weekday_list[p][i][0])
                    
                    #input()
                    try:
                        third += " on a " + weekday_dict[int(weekday_list[p][i][0])]
                        #print(result_summarizers[p][i],result_summarizers[p][i],weekday_list[p])
                        #print(i,j,result_summarizers[p][i][j])
                        #input([result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][0])]])
                        #print(result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][0])])
                        result_summarizers[p][0][i].append(weekday_dict[int(weekday_list[p][i][0])])
                        #print(weekday_list[p][i][0],weekday_list[p])
                        weekday_list[p][i].remove(weekday_list[p][i][0])                        
                    except ValueError:
                        import copy
                        tmp = copy.deepcopy(weekday_list[p][i])
                        tmp_index = None
                        for j in range(len(tmp)):
                            if tmp[j] != '':
                                tmp_index = j
                                break
                        #input([tmp,tmp_index])
                        #print(weekday_list[p])
                        third += " on a " + weekday_dict[int(tmp[tmp_index])]
                        #print(result_summarizers[p][i],result_summarizers[p][i],weekday_list[p])
                        #print(i,j,result_summarizers[p][i][j])
                        #input([result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][tmp_index])]])
                        #print(result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][tmp_index])])
                        result_summarizers[p][0][i].append(weekday_dict[int(weekday_list[p][i][tmp_index])])
                        #print(weekday_list[p][i][0],weekday_list[p])
                        weekday_list[p][i].remove(weekday_list[p][i][tmp_index])                        
                    
                    #weekday_index += 1
                num_summarizers += 1
                #print(third)
            second += third
            third = ""
        
        fourth = ","
        fifth = ""
        #if weekdays != None:
            #input(weekday_list[p])
      
        for i in range(len(summarizers2)):
            if len(summarizers2[i]) == 0:
                continue            
                
            if fourth != "," and i == len(summarizers2)-1:
                fourth += " and"     
            attribute_ = attr_list[i]
            if not weather_flag:
                attribute_ = attribute_.lower()
            elif "close value" in attr_:
                tmp = attribute_.split(" ")
                tmp[0] = tmp[0].upper()
                tmp_str = ""
                for j in range(len(tmp)):
                    tmp_str += tmp[j]
                    if j != len(tmp)-1:
                        tmp_str += " "
                attribute_ = tmp_str
                
            if attr_list[i] == "breakfast":
                attribute_ = "carbohydrate intake"            
         
            fourth += " " + particle + " " + attribute_ + " tends to be "
            for j in range(len(summarizers2[i])):
                if fifth != "":
                    fifth += ", then "                
                fifth += summarizers2[i][j]
                if weekdays != None:
                    try:
                        fifth += " the next " + weekday_dict[int(weekday_list[p][i][0])]
                        #print(result_summarizers[p][i],result_summarizers[p][i],weekday_list[p])
                        #print(i,j,result_summarizers[p][i][j])
                        #input([result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][0])]])
                        #print(result_summarizers[p][1][i],weekday_dict[int(weekday_list[p][i][0])])
                        result_summarizers[p][1][i].append(weekday_dict[int(weekday_list[p][i][0])])
                        weekday_list[p][i].remove(weekday_list[p][i][0])
                    except ValueError:
                        import copy
                        tmp = copy.deepcopy(weekday_list[p][i])
                        tmp_index = None
                        for k in range(len(tmp)):
                            if tmp[k] != '':
                                tmp_index = k
                                break
                        #print([tmp,tmp_index])
                        #print(i,j,summarizers2[i][j])
                        #print(weekday_list[p][i])
                        #print(fifth)
                        fifth += " the next " + weekday_dict[int(weekday_list[p][i][tmp_index])]
                        #print(result_summarizers[p][i],result_summarizers[p][i],weekday_list[p])
                        #print(i,j,result_summarizers[p][i][j])
                        #input([result_summarizers[p][0][i],weekday_dict[int(weekday_list[p][i][tmp_index])]])
                        
                        #print(result_summarizers[p][1][i],weekday_dict[int(weekday_list[p][i][tmp_index])])
                        result_summarizers[p][1][i].append(weekday_dict[int(weekday_list[p][i][tmp_index])])
                        #print(weekday_list[p][i][0],weekday_list[p])
                        weekday_list[p][i].remove(weekday_list[p][i][tmp_index])                    
                    
                num_summarizers += 1
            fourth += fifth
            fifth = ""            

        if weekdays == None:
            sixth = " the next day."
        else:
            sixth = '.'
                
        summary = first + second + third + fourth + fifth + sixth
        numsum_list.append(num_summarizers)
        summary_list.append(summary)
        proto_cnt += 1      
        
    #if weekdays != None:
        #for item in result_summarizers:
            #print(item) 
        #input()
    
    #input(result_summarizers)
    #input(summary_list) 
    return summary_list, support_list, proto_cnt, numsum_list, result_summarizers
        
def series_clustering(sax_rep,tw_sax_list,window_size,alpha_size=5,flag=None,week_index=None):
    '''
    Inputs:
    - sax_rep: SAX representation of subtime window
    - tw_sax: SAX representation of specified time window
    - window_size: the time window size (default is a week)
    - (DEPRECATED) thres: similarity threshold (default is 4)
    - alpha_size: alphabet size (default is 5)
    
    Outputs clusters found by the Squeezer algorithm
    
    Purpose: find clusters in data based on the Squeezer algorithm
    '''
    # Split SAX representation into chunks
    if flag != None:
        chunked_sax = flag
    else:
        chunked_sax = [list(sax_rep[i:i+window_size]) for i in range(0,len(sax_rep),window_size)]
            
    # Remove days that aren't part of a full week
    if len(chunked_sax[-1]) != len(chunked_sax[0]):
        chunked_sax.remove(chunked_sax[-1])
            
    if week_index == None:
        week_index = len(chunked_sax)-1
    elif week_index < 0:
        week_index += len(chunked_sax)
                    
    # Sample size is fraction of dataset size
    sample_range = range(len(chunked_sax))
    divisor = 10
    flag = False
    
    #input(chunked_sax)
    
    while not flag: # TODO: this can be made easier 
        if not divisor:
            break
        
        sample_size = int(float(len(chunked_sax))/divisor)
            
        # Calculate similarity threshold
        # (adapted from Squeezer: An efficient algorithm for clustering categorical data)
        avg_array = []
        for r in range(divisor):
            sim_array = []
            #input([sample_range,sample_size])
            indices = random.sample(sample_range,sample_size)
            
            data_sample = [chunked_sax[index] for index in indices]
            #input(data_sample)
            
            for i in range(len(data_sample)):
                for j in range(len(data_sample)):
                    if i==j:
                        continue
                    
                    similarity = 0
                    tuple1 = data_sample[i]
                    tuple2 = data_sample[j]
                    
                    for k in range(len(tuple1)):
                        similarity += (tuple1[k] == tuple2[k])
                        
                    sim_array.append(similarity)
            
            if len(sim_array) != 0:
                flag = True
            else:
                divisor -= 1
                break
            avg_array.append(float(sum(sim_array))/len(sim_array))
            
            
    thres = float(sum(avg_array))/len(avg_array) + 1
    #thres = 1.3
    
    # Find relevant cluster
    clusters = squeezer(np.array(chunked_sax),thres) 
    for i in range(len(clusters)):
        clusters[i] = [x for x in clusters[i] if x <= week_index]
        
    import copy
    clusters_ = copy.deepcopy(clusters)
    
    max_index = 0
    for i in range(len(clusters)):
        for j in range(len(clusters[i])):
            if clusters[i][j] > max_index:
                max_index = clusters[i][j]
                
    if max_index < week_index and week_index == len(tw_sax_list)-1:
        week_index = max_index
    
    #print(max_index)
    #print(week_index)
    #input(clusters)
    cluster_data = None
    for cluster in clusters:
        if week_index in cluster:
            cluster_data = cluster
            break
    #input(cluster_data)
    if cluster_data == None:
        #input(clusters)
        return None

    #print(week_index, clusters)

    # Remove TW of interest
    #print(clusters_)
    cluster_data.remove(week_index)
    #input(clusters_)
    #cluster_data = cluster_data[:-1]
    if len(cluster_data) == 0:
        return None
    
    indices = cluster_data
    #input(indices)
    
    clusters = []    
    
    for j in range(len(tw_sax_list)):
        subclusters = []
        for i in range(len(cluster_data)):
            #input([cluster_data[i]+1,len(cluster)])
            if cluster_data[i]+1 >= len(tw_sax_list[j]):
                continue
            
            try:
                subclusters.append([tw_sax_list[j][cluster_data[i]],tw_sax_list[j][cluster_data[i]+1]])
            except IndexError:
                print("cluster index error")
                input([tw_sax_list[j],cluster_data[i]])
                
        
        if len(subclusters) != 0:
            clusters.append(subclusters)

    if len(clusters) == 0:
        return None
    
    return [clusters, indices, week_index, clusters_]

def standard_pattern_summary(first_letters,second_letters,attr_list,tw_index,singular_TW="week"):
    summarizer_type = "Standard Pattern"
    summarizer_list = []
    for i in range(len(first_letters)):
        first_letter = first_letters[i]
        second_letter = second_letters[i]
        
        if first_letter < second_letter:
            summarizer = "rose"
        elif first_letter > second_letter:
            summarizer = "dropped"
        else:
            summarizer = "stayed the same"
            
        summarizer_list.append(summarizer)
    
    return get_protoform(summarizer_type,attr_list,None,summarizer_list,singular_TW+"s",tw_index=tw_index), summarizer_list

def display_clusters(data,clusters,window_size=7):
    '''
    Inputs:
    - data: the raw data
    - clusters: clusters found using find_similar_tw
    - window_size: the time window size (default is a week)
    
    Outputs: None
    
    Purpose: Displays clusters over the raw data using different colors
    '''
    # Modify data to pair each time series with its index
    for i in range(len(data)):
        data[i] = [i,data[i]]    
            
    #https://stackoverflow.com/questions/17240694/python-how-to-plot-one-line-in-different-colors
    fig, ax = plt.subplots()
    colors = []
    
    # Generate list of random colors (# of clusters + rest of data)
    for i in range(len(clusters)+1):
        colors.append(tuple([np.random.uniform(),np.random.uniform(),np.random.uniform()]))
      
    for i in range(len(data)-window_size):
        plt.axvline(x=i,color='k',linewidth=0.05)
        
        # Get start and stop days
        days = []        
        for j in range(window_size+1):   
            days.append(data[i+j])
        
        # Get ranges in data for colors and plot them
        for start,stop in zip(days[:-1],days[1:]):
            x,y = zip(start,stop)
            color_index = -1
            for j in range(len(clusters)):
                if i in clusters[j]:
                    color_index = j

            ax.plot(x,y,color=colors[color_index])
            
    plt.show()

def find_similar_tw(data,tw_sax,window_size=7,alpha_size=5,dist='mindist'):
    '''
    Inputs:
    - data: the raw data
    - tw_sax: the SAX representation of the past tw
    - window_size: the time window size (default is a week)
    - alpha_size: the alphabet size (default is 5)
    - dist: the distance function used (default is Keogh's MINDIST)
    
    Outputs:
    - tw_comparisons: a list of the clusters
    - indices: the indices where the time windows in the clusters are in the data
    
    Purpose: find clusters in the data using SAX representation
    '''
    # Get weekly patterns
    tw_patterns = sax_via_window(data,window_size,window_size,alpha_size,dist)
    last_index = len(data) - (window_size+1)
    other_tw = []
    indices = []
    
    # Find grouping with current week and set other_weeks to that grouping
    # minus the current week
    for key in tw_patterns.keys():
        if tw_patterns[key] == 6:
            display_clusters(data,tw_patterns[key])
        if last_index in tw_patterns[key]:
            indices = [tw_patterns[key]]
            other_tw = tw_patterns[key][:-1]
            break
                    
    tw_comparisons = [] 
    for i in range(len(other_tw)):
        tw_letter = tw_sax[other_tw[i]/window_size]
        next_tw = tw_sax[(other_tw[i]+window_size)/window_size]
        
        tw_comparisons.append([tw_letter,next_tw])   
    
    return tw_comparisons, indices

####### HELPER FUNCTIONS #######

def unique_color():
    '''
    Inputs: None
    
    Outputs: None
    
    Purpose: Generates a random color
    '''
    #https://stackoverflow.com/questions/17240694/python-how-to-plot-one-line-in-different-colors
    return plt.cm.gist_ncar(np.random.random())

def get_cluster_index(num,clusters,tw=7):
    '''
    Inputs: 
    - num: the number to be looked for in a cluster
    - clusters: the list of clusters
    - tw: the time window size (default is a week)
    
    Outputs the index of the cluster
    
    Purpose: Find the appropriate cluster
    '''
    for i in range(len(clusters)):
        if clusters[i] == num:
            return i
    return -1

def mindist(sax_rep,sax_rep2):
    '''
    Inputs:
    - sax_rep: first SAX representation
    - sax_rep2: second SAX representation
    
    Outputs the distance between the two SAX representations
    
    Purpose: Implementation of Keogh's MINDIST function
    '''
    summation = 0
    for i in range(len(sax_rep)):
        dist = letter_dist(sax_rep[i],sax_rep2[i])
        sq_dist = dist**2
        summation += sq_dist
    summ_sq = math.sqrt(summation)
    return math.sqrt(len(df_list[df_index])/len(sax_rep))*summ_sq   

def progressive_dec(sax_rep):
    '''
    Inputs:
    - sax_rep: first SAX representation
    
    Outputs whether there is a progressive decrease
    '''
    
    #dec = True
    cnt = 0
    for i in range(len(sax_rep)-1):
        if sax_rep[i] <= sax_rep[i+1]:
            cnt += 1
    
    return float(cnt)/len(sax_rep)

def generateOWLTriples(ada_goal):
    if ada_goal == "consistentcarb":
        name = ":ConsistentCarbDietPattern"
        valuesFrom = "owl:someValuesFrom [ owl:intersectionOf ( :Carbohydrate"
        valuesFrom += " :Adherence"
        valuesFrom += " :Frequency"
        valuesFrom += " ) ;"
        valuesFrom += " rdf:type owl:Class"
        valuesFrom += " ]"
        
    elif ada_goal == "highcarblowfat":
        name = ":HighCarbLowFatDietPattern"
        valuesFrom = "owl:allValuesFrom [ owl:intersectionOf ( :HighCarb"
        valuesFrom += " :LowFat"
        valuesFrom += " :Adherence"
        valuesFrom += " :Frequency"
        valuesFrom += " ) ;"
        valuesFrom += " rdf:type owl:Class"
        valuesFrom += " ]"
        
        #valuesFrom += "]"
        #valuesFrom += ") ;"
    elif ada_goal == "lowcarb":
        name = ":LowCarbDietPattern"
        valuesFrom = "owl:allValuesFrom [ owl:intersectionOf ( :LowCarb"
        valuesFrom += " :Adherence"
        valuesFrom += " :Frequency"
        valuesFrom += " ) ;"
        valuesFrom += " rdf:type owl:Class"
        valuesFrom += " ]"
        
    elif ada_goal == "fat percentage":
        name = ":IdealTotalFatDietPattern"
        valuesFrom = "owl:allValuesFrom [ owl:intersectionOf ( :IdealTotalFat"
        valuesFrom += " :Adherence"
        valuesFrom += " :Frequency"
        valuesFrom += " ) ;"
        valuesFrom += " rdf:type owl:Class"
        valuesFrom += " ]"
    else: 
        return
        
    output_str = name + " rdf:type owl:NamedIndividual ,"
    output_str += "[ owl:intersectionOf ( :ConsistentPattern"
    output_str += "[ rdf:type owl:Restriction ;"
    output_str += " owl:onProperty <http://semanticscience.org/resource/SIO_000008> ;"
    output_str += " " + valuesFrom + ""
    output_str += "]"
    output_str += ") ;"
    output_str += "  rdf:type owl:Class"
    output_str += "] ."
    
    
    return output_str
    
def getSAX(data):
    pass

def getTruthValue(summary,sax):
    summarizer_map = {"very low" : "a",
                      "low" : "b",
                      "moderate" : "c",
                      "high" : "d",
                      "very high" : "e"}
    sax_map = {1 : "a",
               2 : "b",
               3 : "c",
               4 : "d",
               5 : "e"}

    if type(summary) is str:
        summary = summary.split(' ')
        
    try:
        q_index = summary.index("of")-1
    except:
        return 0.0
        
    quantifier = ' '.join(summary[q_index:q_index+3])        
    summarizer = summary[-1].strip('.')
    if summarizer not in summarizer_map.keys():
        return 0.0
        
    letter = summarizer_map[summarizer]
    try:
        ratio = float(sax.count(letter))/len(sax)
    except:
        sax = sax.int()
        sax = [sax_map[x.item()] for x in sax]
        ratio = float(sax.count(letter))/len(sax)
    
    truth = round(get_muQ(quantifier,ratio),2) 
    return max(float(truth),0.0)