""" 
Alternative approach:

From "Fuzzy linguistic summaries of databases for an
efficient business data analysis and decision support" paper

V is a quality (attribute) of interest -> step counts
Y = {y1,...,yN} is a set of objects (records) that manifest quality V,
e.g., the set of days; hence V(yi) are values of quality V for object yi
D = {V(y1),...,V(yN)} is a set of data ("database") -> set of step counts

A summary of a data set consists of:
- A summarizer S (e.g. "enough steps in a day" vs "not enough steps")
- a quantity in agreement Q (e.g. "most")
- truth (validity) T, e.g., T(On most days, you reached the American Heart Assocation's recommended number of 10,000 steps per day.)

For summarizer S in terms of step counts, it would only be "enough steps in a day"
if the day's step count is at or over 10,000 steps. Otherwise, it would be 
"not enough steps in a day". The 10,000 benchmark would make the quantity absolute,
as opposed to relative.

More complicated summaries include combinations of attributes using a hierarchy or
other methods (unsure how this would apply to step counts but it could be useful 
when looking at multiple attributes such as the response to "How am I doing?")

For "Qy's are F", Q is a linguistic quantifier, y is a member of Y (the set of 
days), and F is a property (e.g., passing, in terms of step count)

In the case where Q = "most", muQ(x) will be 1 if x is greater than half of the number of days in the time window (TW) or muQ(x) will be 0 otherwise. 

muF(yi) will be 1 if day yi has a step count at or over 10,000 steps. It will be
0 otherwise. Thus, truth(Qy's are F) = muQ((1/n)*sum_i=1...n(muF(yi))). In other
words, there will be a sum of 1's and 0's pertaining to the days in the TW that
will be averaged. The average will then be inputted as x into the muQ membership
function.

muWg is for the membership function value of the query, basically measuring how
well the data matches the query. This is compared to the muS because the summary
may be stating facts about data that is less relevant to the query.
==================================================
Set time window (TW)
Go through data in time window and fill database 

Database contains:
Number of "good" days in TW
Average step count over TW
Best/Worst day or outliers (boxplot?)


Set step_quantifier based on data


"On most days in the past [specified time window (last week is default)],
you [step_quantifier] the American Heart Assocation's recommended number of 
10,000 steps per day."

Other ideas:
- Based on user's performance, you can add suggestions to help increase step count
or ask what happened
     - Add suggestions only if the user is continuing to struggle with step counts
     - Ask what happened if the user is not performing as well as previous TWs
- Compare with other TWs

Or do all of this and rank the results to see which ones are more interesting
or helpful

Citation:
 Senin, P., Lin, J., Wang, X., Oates, T., Gandhi, S., Boedihardjo, A.P., Chen, C., Frankenstein, S., Lerner, M., GrammarViz 2.0: a tool for grammar-based pattern discovery in time series, ECML/PKDD Conference, 2014.
"""

import math
import os
import pandas as pd
from saxpy.sax import sax_via_window
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime
####### GENERAL SUMMARY FUNCTIONS #######

def get_protoform(summarizer_type,attr,best_quantifier,summarizer,TW="weeks",x_val="days"):
    singular_TW = TW[:-1]
    if summarizer_type == "Step Counts":
        return "On " + str(best_quantifier) + " days in the past " + singular_TW + ", you " + str(summarizer) + " the American Heart Association's recommended number of 10,000 steps per day."        
    elif summarizer_type == "Heart Rate":
        return "On " + str(best_quantifier) + " days in the past " + singular_TW + ", you " + str(summarizer) + " your goal to stay within your heart rate range." 
    elif summarizer_type == "Calorie Intake":
            return "On " + str(best_quantifier) + " days in the past " + singular_TW + ", you " + str(summarizer) + " your goal to stay under 2,000 calories."     
    elif summarizer_type == "Trends":
        return str(best_quantifier).capitalize() + " time, your " + attr.lower() + " " + str(summarizer) + " from one day to the next."
    elif "Past Daily Week" in summarizer_type:
        if attr == "Activity":
            return "Over " + str(best_quantifier) + " " + x_val + " in the past " + singular_TW + " have been " + str(summarizer) + "."
        return "Over " + str(best_quantifier) + " " + x_val + " in the past " + singular_TW + ", your " + attr.lower() + " has been " + str(summarizer) + "."
    elif "Pattern Recognition" in summarizer_type:
        return "When " + str(best_quantifier) + " " + TW + " similar to this past one occurred, your " + attr.lower() + " " + str(summarizer) + " the next " + singular_TW + "."
    else:
        return ""

def generate_summaries(summarizers,summarizer_type,attr,data,letter_map,alpha_size,TW="weeks",age=None,activity_level=None,xval = None):
    """
    Inputs:
    - summarizers: the list of relevant summarizers
    - summarizer_type: the type of summarizer
    - data: the time series
    - TW: the time window (default is "the past week"
    
    Outputs:
    - output_list: A list of lists containing the t1 truth values in one list 
    and the generated summaries in another
    
    Purpose: To generate the summaries based on the inputted summarizers that will
    dictate which quantifiers will be best for the sentence.
    """
    
    t1_list = []
    summary_list = []
    best_quantifiers = []
        
    # Error check
    if len(data) == 0:
        return [None,None,None]
    
    for summarizer in summarizers:
        
        # Use the get_muS to grab the membership function value for the summarizer
        # based on the step count value for the day
        average = 0
        for data_point in data:
            if age != None and activity_level != None:
                muS = get_muS(summarizer_type,summarizer,data_point,letter_map,alpha_size,age,activity_level)
            else:
                muS = get_muS(summarizer_type,summarizer,data_point,letter_map,alpha_size)
                
            # Error check for get_muS
            if muS == -1:
                return [None,None,None]
             
            average += muS
             
        average = float(average)/len(data)
        # Uses the getQForS function to find the best quantifier based on the 
        # inputted proportion of days that have a good step count
        best_quantifier = getQForS(average)
        
        # Error check for getQForS function
        if best_quantifier == -1:
            return [None,None,None]
        
        # Using the summarizers and their best quantifiers, summaries are generated
        summary = get_protoform(summarizer_type,attr,best_quantifier,summarizer,TW=TW,x_val=xval)
        
        if len(summary) == 0:
            return [None,None,None]
        
        #t1 = zadeh_truth(best_quantifier,average)
        t1 = average
        
        summary_list.append(summary)
        t1_list.append(t1)
        best_quantifiers.append(best_quantifier)
        
    output_list = [t1_list,best_quantifiers,summary_list]
    
    return output_list
            
def get_muS(summarizer_type,summarizer,value,letter_map,alpha_size,age=None,activity_level=None):
    """
    Inputs: 
    - summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - summarizer: the summarizer
    - value: the value obtained from the database
    
    Outputs: The membership function value of the summarizer based on the
    inputted value and the summarizer type; -1 if summarizer_type is not found
    
    Purpose: To find and return the membership function value of the summarizer
    based on the inputted value and the summarizer type
    """
    if summarizer_type == "Step Counts":
        if summarizer == "reached":
            return int(value >= 10000)
        else:          
            return int(value < 10000)
    if summarizer_type == "Heart Rate":
        if summarizer == "reached":
            return int(hr_evaluation(value,age,activity_level) == "within range")
        else:
            return int(hr_evaluation(value,age,activity_level) != "within range")
    if summarizer_type == "Calorie Intake":
        if summarizer == "reached":
            return int(value < 2000)
        else:
            return int(value >= 2000)        
    if summarizer_type == "Stock":
            if summarizer == "reached":
                return int(value >= 200)
            else:
                return int(value < 200)    
    elif summarizer_type == "Trends":
        if summarizer == "increases":
            return int(value > 0)
        elif summarizer == "decreases":
            return int(value < 0)
        else:
            return int(value == 0)
    elif "Past Daily Week" in summarizer_type:
        if "Heart Rate" in summarizer_type:
            return int(hr_evaluation(value,age,activity_level) == summarizer)
        if "Activity" in summarizer_type:
            return int(categ_eval(value) == summarizer)        
        return int(evaluateSAX(value,letter_map,alpha_size) == summarizer)
    elif "Pattern Recognition" in summarizer_type:
        if summarizer == "rose":
            return int(value[0] < value[1])
        elif summarizer == "dropped":
            return int(value[0] > value[1])
        else:
            return int(value[0] == value[1])
        
    return -1

def getQForS(value):
    """
    Inputs:
    - (DEPRECATED) summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - value: the x for muQ(x)
    
    Outputs: Returns the membership function value for the quantifier based on
    the summarizer type and the inputted value; -1 if summarizer_type is not 
    found
    
    Purpose: to return the membership function value for the quantifier based on
    the summarizer type and the inputted value
    """
    
    # Value is expected to be in [0,1]
    # ["all of the","most","more than half of the", "half of the","some of the","none of the"]
    if value == 0:
        return "none of the"
    elif value < 0.2:
        return "almost none of the"
    elif value < 0.5:
        return "some of the"
    elif value == 0.5:
        return "half of the"
    elif value < 0.75:
        return "more than half of the"
    elif value < 1:
        return "most of the"
    else:
        return "all of the"
        
    return -1        

####### SAX SUMMARY FUNCTIONS #######

def get_single_SAX_summary(summarizer_type,attr,letter,letter_map,alpha_size,flag=None):
    conclusion = evaluateSAX(letter,letter_map,alpha_size)
    if attr == "Step Counts":
        attr = "step count"
        
    return ("In the past week, your " + attr.lower() + " has been " + conclusion + ".", conclusion)
    
def comparison_SAX_summary(summarizer_type,attr,prev_letter,curr_letter,other_week_index=None,tw=None):
    summarizer = None
    goal = None
    
    if attr == "Stock" or attr == "Step Counts":    
        goal = "high"
        
    elif attr == "Calorie Intake":
        goal = "low"
        
    elif attr == "Heart Rate":
        goal = "within range"
        
    if goal == "high":
        if prev_letter < curr_letter:
            summarizer = "better"
        elif prev_letter == curr_letter:
            summarizer = "about the same"
        else:
            summarizer = "not do as well"   
    elif goal == "low":
        if prev_letter < curr_letter:
            summarizer = "not do as well"
        elif prev_letter == curr_letter:
            summarizer = "about the same"
        else:
            summarizer = "better"   
            
    if summarizer == None:
        return None
            
    if other_week_index != None and tw != None:
        return "You did " + summarizer.lower() + " with keeping your " + attr.lower() + " " + goal + " than you did on the week starting on day " + str(tw*other_week_index) + "."
    
    return "You did " + summarizer.lower() + " with keeping your " + attr.lower() + " " + goal + " than you did the week before."

####### OTHER SAX FUNCTIONS #######

def letter_dist(q_i,c_i):
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

def evaluateSAX(letter,letter_map,alpha_size,flag=None):
    summarizer_5_map = {1 : "very low",
                          2 : "low",
                          3 : "moderate",
                          4 : "high",
                          5 : "very high"}      
    
    summarizer_3_map = {1 : "low",
                        2 : "moderate",
                        3 : "high"
                        }       
        
    summarizer_2_map = {1 : "low",
                        2 : "high"}    
    
    value = letter_map[letter]
    if flag == "HR":
        summarizer_map = {1 : "abnormally low",
                          2 : "low",
                          3 : "within range",
                          4 : "high",
                          5 : "abnormally high"} 
        return summarizer_map[value+1]
    
    if flag == "ACT":
        summarizer_map = {
            1 : "walking",
            2 : "inactive",
            3 : "in a vehicle"
        }
    
    # Choose bucket the value fits in
    
    summarizer_map = None
    if alpha_size > 1:
        summarizer_map = summarizer_2_map
    if alpha_size > 2:
            summarizer_map = summarizer_3_map    
    if alpha_size > 3:
            summarizer_map = summarizer_5_map    
            
    bucket_size = alpha_size/len(summarizer_map.keys())
    
    #print letter, letter_map[letter]
    #raw_input()
    
    bucket = int(math.floor(float(value)/float(bucket_size)))
    if bucket == 0:
        bucket = 1
    
    return summarizer_map[bucket]
    

def best_quantifier_index(quantifiers,truths):
    quant_map = {"none of the" : 1,
                 "almost none of the" : 2,
                 "some of the" : 3,
                 "half of the" : 4,
                 "more than half of the" : 5,
                 "most of the" : 6,
                 "all of the" : 7
                 }
    
    values = []
    for i in range(len(quantifiers)):
        values.append(quant_map[quantifiers[i]])
    
    truth = 0
    index = 0
    #print values
    #raw_input()
    if values.count(max(values)) > 1:
        for i in range(len(values)):
            if values[i] == max(values):
                if truths[i] > truth:
                    truth = truths[i]
                    index = i
    else:
        index = values.index(max(values))
                    
    #raw_input(index)
    return index

####### SUMMARY EVALUATION FUNCTIONS #######

def zadeh_truth(quantifier,x):
    """
    Inputs: 
    - (DEPRECATED) summarizer_type: the domain of the summarizer we are looking at (e.g., step counts)
    - quantifier: the quantifier dictating which membership function to use
    - x: the value of the proportion after average of the muF
    
    Outputs: Returns the truth value of the summary based on Zadeh's calculus; -1
    if summarizer_type not found
    
    Purpose: To calculate the truth value of the summary based on Zadeh's calculus
    """
    
    if quantifier == "none of the":
        if x >= 0 and x <= 0.1:
            return -10*x + 1
        else:
            return 0        
        
    elif quantifier == "almost none of the":
        if x > 0 and x <= 0.1:
            return 10*x
        elif x > 0.1 and x <= 0.2:
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
        elif x > 0.75 and x <= 0.9:
            return 1
        elif x > 0.9 and x < 1:
            return -10*x + 10
        else:
            return 0
            
    elif quantifier == "all of the":
        if x > 0.9 and x < 1:
            return 10*x - 9
        elif x == 1:
            return 1
        else:
            return 0
    
    return -1

####### USER EVALUATION FUNCTIONS #######

def goal_evaluation(goal,values):
    target_map = None
    if goal == "FSC":
        target_map = {"protein" : 50,
                          "fat" : 70,
                          "sat_fat" : 24,
                          "carbs" : 310,
                          "sugar" : 90,
                          "sodium" : 2.3,
                          "fiber" : 30}        
    
    results = []
    for key in values.keys():
        if key in target_map:
            if values[key] < target_map[key]:
                results.append([key,"inc"])
            elif values[key] > target_map[key]:
                results.append([key,"dec"])
                
    return results

def HR_Summary(heart_rate, age, activity_level):
    conclusion = hr_evaluation(heart_rate, age, activity_level)
    return "In the past week, your heart rate has been " + conclusion + "."

def hr_evaluation(heart_rate, age, activity_level):
    
    if age >= 18:
        lower_bound = 60
    else:
        lower_bound = 70
        
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
        
def comparison_HR_summary(last_week,curr_week,age,activity_level):
    l_cnt = 0
    c_cnt = 0
    goal = "within range"
    for i in range(len(last_week)):
        if hr_evaluation(last_week[i],age,activity_level) == goal:
            l_cnt += 1
        if hr_evaluation(curr_week[i],age,activity_level) == goal:
            c_cnt += 1    
            
    summarizer = None
    if l_cnt > c_cnt:
        summarizer = "not do as well"
    elif l_cnt < c_cnt:
        summarizer = "better"
    else:
        summarizer = "about the same"
        
    return "You did " + summarizer.lower() + " with keeping your heart rate within range than you did the week before."

def categ_eval(letter):
    activity_map = {
        "w" : "walking",
        "s" : "inactive",
        "v" : "in a vehicle"
    }
    
    return activity_map[letter]

def comparison_activ(prev_day,curr_day,other_index=None):
    prev = prev_day.count("w")
    curr = curr_day.count("w")
    
    if prev > curr:
        summarizer = "less"
        pair_word = "than"
    elif prev < curr:
        summarizer = "more"
        pair_word = "than"        
    else:
        summarizer = "just as"
        pair_word = "as"        
        
    if other_index != None:
        return "You were " + summarizer + " active " + pair_word + " you were on day " + str(other_index+1) + "."
    
    return "You were " + summarizer + " active " + pair_word + " you were the previous day."

####### DATA FUNCTIONS #######

def get_data_list(index_list,dataset):
    df_list = []
    if dataset == "Stock Market Data":
        data_folder = "data/Stock Market Data"
        columns = ['Volume','Close','High','Open','Low']
        column = 'Close'
    elif dataset == "Heart Rate" or dataset == "Step Counts" or dataset == "ActivFit":
        data_folder = "data/Insight4Wear"
        columns = ['Step Counts','Heart Rate']
        if dataset == "ActivFit":
            columns = ["date","ActivFit"]
        column = dataset
    elif dataset == "Calorie Intake":
        data_folder = "data/Food Data"
        columns = ["calories"]
        column = "calories"
        
    csv_list = os.listdir(data_folder)
    
    days = []
    
    for i in range(len(index_list)):
        
        data_index = index_list[i]
        
        df = pd.read_csv(data_folder + "/" + csv_list[data_index])
        
        if dataset != "ActivFit":
            df.set_index('date',inplace=True)
        
        df.columns = columns
        if dataset != "ActivFit":
            if len(days) == 0:
                days = df['date']
            values = df[column].tolist()
        else:
            days = df['date']
        if column == dataset or column == "calorie":
            if dataset == "Heart Rate":
                values = [x for x in values if not math.isnan(x)]
            elif dataset == "Step Counts":
                values = values[124:362]
                values.pop(101)
            elif dataset == "ActivFit":
                values = df
            else:
                values = df[column].tolist()

        df_list.append(values)  
        
        if dataset == "ActivFit":
            ticks = []
            curr_date = None
            values = df[column]
            #raw_input(days[0])
            for i in range(len(days)):
                date = datetime.strptime(days[i],"%Y-%m-%d %H:%M:%S")
                #date = date.strip(" ")
                #date = date[0]
                date_str = str(date.month) + "/" + str(date.day) + "/" + str(date.year)
                #raw_input(date_str)
                if date_str != curr_date:
                    curr_date = date_str
                    ticks.append(i)
                
        #raw_input(values)
        #print days
        #raw_input()
        #if i==0:
            #fig, ax .= plt.subplots()
        if dataset == "ActivFit":
            plt.xticks(ticks,[x for x in range(len(ticks))])
            plt.plot(values,linestyle='-')
            plt.xlabel("Days")
            plt.ylabel("Activity")
    
    plt.show()
    return df_list

def create_database(sax,letter_map,tw,alpha_size,prefix):
    
    db_filename = prefix + ".ascii"
    data_file = open(db_filename,"w")
    seq_id = 1
    evt_id = 1
    
    for i in range(0,len(sax),tw):
        substring = sax[i:i+tw]
        for j in range(0,len(substring)):
            line = str(seq_id) + " " + str(j+1) + " 1 " + str(letter_map[substring[j]]) + '\n'
            ascii = line.encode('ascii')
            data_file.write(line)
            evt_id += 1
        seq_id += 1

    data_file.close()
    
def parse_patterns(content):
    
    # Parse patterns
    for i in range(len(content)):
        content[i] = content[i].strip('\n')
        content[i] = content[i].split(' -- ')
        content[i] = content[i][:-1]
        content[i] = content[i][0].split(' -> ')
    
    # Remove 1-sequences
    content = [seq for seq in content if len(seq) > 1]
    
    return content
     
def get_patterns(sax,letter_map,tw,alpha_size,prefix,path,cygwin_path):
    
    # Create a data file for CSPADE
    create_database(sax,letter_map,tw,alpha_size,prefix)    
    
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
    exttpose = [path + "exttpose.exe", "-i", file_path, "-o", file_path, "-l", "-s", "0", "-x"]
    subprocess.check_output(exttpose,stderr=subprocess.STDOUT) 

    # Get sequences and output them to patterns.txt file
    spade = [path + "spade.exe", "-e", "1", "-i", file_path, "-s", "0.4", "-o", "-w", "7", "-u", "1"]
    output_file = open(path + "patterns.txt","w")
    subprocess.call(spade,stdout=output_file)
    output_file.close()    
    
    os.chdir(path)
    
    with open("patterns.txt","r") as patterns_file:
        content = patterns_file.readlines()
        
    content = content[2:]
    return parse_patterns(content)

def analyze_patterns(summarizer_type,sax,alphabet,letter_map,tw,alpha_size,prefix,path,cygwin_path,proto_cnt,flag_=None):
    
    patterns = get_patterns(sax,letter_map,tw,alpha_size,prefix,path,cygwin_path)
    summarizer_type = summarizer_type[0].lower() + summarizer_type[1:]
    
    pattern_dict = dict()
    prefix_cnt = dict()
    
    string_patterns = []
    for pattern in patterns:
        string_patterns.append(''.join(pattern))
        
    index = 1 
    cnt = -1
    min_conf = 0.8
    while cnt != 0:
        cnt = 0
        for item in string_patterns:
            prefix = item[:index]
            suffix = item[index:]
            
            if len(suffix) == 0:
                continue
            
            if prefix not in pattern_dict.keys():
                pattern_dict[prefix] = dict()
              
            if prefix not in prefix_cnt.keys():
                prefix_cnt[prefix] = 0           
            
            subsuffix = ""
            for i in range(len(suffix)):
                subsuffix += suffix[i]
                if subsuffix not in pattern_dict[prefix].keys():
                    pattern_dict[prefix][subsuffix] = 1
                else:
                    pattern_dict[prefix][subsuffix] += 1
                prefix_cnt[prefix] += 1
        
            cnt += 1
            
        index += 1
        
    freq_patterns = []
    for key in pattern_dict.keys():
        for subkey in pattern_dict[key].keys():
            pattern_dict[key][subkey] = float(pattern_dict[key][subkey])/float(prefix_cnt[key])
            freq_patterns.append([key,subkey,pattern_dict[key][subkey]])
                     
    freq_patterns = sorted(freq_patterns,key = lambda x: x[2],reverse=True)
    index = 0
    for i in range(len(freq_patterns)):
        if freq_patterns[i][2] <= min_conf:
            index = i
            break
        
    freq_patterns = freq_patterns[:index]
    
    if len(freq_patterns) != 0:
        print "I have found some patterns for you:"    
        
    # Focusing on next day only at the moment
    for pattern in freq_patterns:
        prefix = pattern[0]
        suffix = pattern[1]
        conf = float(pattern[2])
                
        letters1 = []
        letters2 = []
        for i in range(len(prefix)):
            letters1.append(alphabet[int(prefix[i])-1])
            
        for i in range(len(suffix)):
            letters2.append(alphabet[int(suffix[i])-1])
        
        summarizers1 = []
        summarizers2 = []
        for i in range(len(letters1)):
            summarizers1.append(evaluateSAX(letters1[i],letter_map,alpha_size,flag=flag_))
        for i in range(len(letters2)):
            summarizers2.append(evaluateSAX(letters2[i],letter_map,alpha_size,flag=flag_))
            
        if summarizer_type[-1] == "s":
            summarizer_type = summarizer_type[:-1]
            
        first = "There is " + str(int(conf*100)) + "% confidence that, when your " + summarizer_type.lower() + " follows the pattern of being "
        second = ""
        for i in range(len(summarizers1)):
            second += summarizers1[i]
            if i != len(summarizers1)-1:
                second += ", then "
        
        third = ", it tends to be " 
        fourth = ""
        for i in range(len(summarizers2)):
            fourth += summarizers2[i]
            if i != len(summarizers2)-1:
                fourth += ", then "
        fifth = " the next day."
                
                
        summary = first + second + third + fourth + fifth
        print summary
        proto_cnt += 1        
                
        #raw_input(first + second + third + fourth)
        
            
        #raw_input([summarizers1,summarizers2])
            
        #if summarizer1 not in pattern_dict.keys():
            #pattern_dict[summarizer1] = dict()
        #else:
            #if summarizer2 not in pattern_dict[summarizer1].keys():
                #pattern_dict[summarizer1][summarizer2] = 1
            #else:
                #pattern_dict[summarizer1][summarizer2] += 1
                        
    
            
    # Get summaries
    #for summarizer1 in pattern_dict.keys():
        #max_val = 0
        #best_summarizer = None
        
        ## Find most frequent summarizer
        #for summarizer2 in pattern_dict[summarizer1].keys():
            #if pattern_dict[summarizer1][summarizer2] > max_val:
                #max_val = pattern_dict[summarizer1][summarizer2]
                #best_summarizer = summarizer2
                
        #prefix = "Whenever your " + summarizer_type.lower() + " is " + summarizer1 + ", it tends to "
        #summary = ""
        #if summarizer1 == summarizer2:
            #summary = prefix + "stay the same"
        #else:
            #summary = prefix + "become " + summarizer2
            
        #summary = summary + " the next day"
        #print summary
        #proto_cnt += 1
        
    return proto_cnt
        
def within_series_clustering(data,window_size=7,thres=4,alpha_size=5):
        
    # Get SAX representation
    sax_rep = ts_to_string(znorm(np.array(data)), cuts_for_asize(alpha_size))
    
    # Split SAX representation into chunks
    chunked_sax = [list(sax_rep[i:i+window_size]) for i in range(0,len(sax_rep),window_size)]
    
    # Remove days that aren't part of a full week
    if len(chunked_sax[-1]) != len(chunked_sax[0]):
        chunked_sax.remove(chunked_sax[-1])

    return squeezer(np.array(chunked_sax),thres)      

def display_clusters(data,clusters,window_size=7):
    
    # Modify data to pair each time series with its index
    for i in range(len(data)):
        data[i] = [i,data[i]]    
            
    #https://stackoverflow.com/questions/17240694/python-how-to-plot-one-line-in-different-colors
    fig, ax = plt.subplots()
    colors = []
    
    # Generate list of random colors
    for i in range(len(clusters)):
        colors.append(tuple([np.random.uniform(),np.random.uniform(),np.random.uniform()]))
      
    for i in range(0,len(data),window_size):
        plt.axvline(x=i,color='k',linewidth=0.05)
        week_num = int(i/7)
        
        if week_num >= len(data)/window_size:
            break
        
        days = []
        # Get start and stop days
        for j in range(window_size+1):   
            days.append(data[i+j])
        
        # Get ranges in data for colors
        for start,stop in zip(days[:-1],days[1:]):
            x,y = zip(start,stop)
            cluster_index = get_cluster_index(week_num,clusters)
            ax.plot(x,y,color=colors[cluster_index])
            
    plt.show()   

def find_similar_weeks(data,week_sax,window_size=7,alpha_size=5,dist='mindist'):
    
    # Get weekly patterns
    weekly_patterns = sax_via_window(data,window_size,window_size,alpha_size,dist)
    last_index = len(data) - (window_size+1)
    other_weeks = []
        
    # Find grouping with current week and set other_weeks to that grouping
    # minus the current week
    for key in weekly_patterns.keys():
        if last_index in weekly_patterns[key]:
            other_weeks = weekly_patterns[key][:-1]
            break
                    
    week_comparisons = [] 
    for i in range(len(other_weeks)):
        week_letter = week_sax[other_weeks[i]/window_size]
        next_week = week_sax[(other_weeks[i]+window_size)/window_size]
        
        week_comparisons.append([week_letter,next_week])   
    
    return week_comparisons

####### HELPER FUNCTIONS #######

def unique_color():
    #https://stackoverflow.com/questions/17240694/python-how-to-plot-one-line-in-different-colors
    return plt.cm.gist_ncar(np.random.random())

def get_cluster_index(num,clusters):
    for i in range(len(clusters)):
        if num in clusters[i]:
            return i
    return -1

def mindist(sax_rep,sax_rep2):
    summation = 0
    for i in range(len(sax_rep)):
        dist = letter_dist(sax_rep[i],sax_rep2[i])
        sq_dist = dist**2
        summation += sq_dist
    summ_sq = math.sqrt(summation)
    return math.sqrt(len(df_list[df_index])/len(sax_rep))*summ_sq   