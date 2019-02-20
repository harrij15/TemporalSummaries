# Temporal Summaries

## Defined Terms

- Protoform (P): A sentence prototype (or template) that can be used to generate a natural language summary once it is filled in with the necessary information
- Summarizer (S): A conclusive phrase for the summary
- Quantifier (Q): A word or phrase that specifies how often the summarizer is true, given the object of interest
- Attribute (A): A variable of interest in the database
- Time window (TW): A time window of interest
- Sub-time window (sTW): A time window at a smaller granularity than the specified time window

## Framework

Our framework automatically generates a diverse set of natural language summaries of time-series data, where the linguistic structure of the summaries conform to a set of protoforms. A protoform is a template that can be used to generate a natural language statement once it is filled in with the necessary information [4,5,6,7]. As an example, a simple protoform is:

> "On (**quantifier**) (**sub-time window**) in the past (**time window**), your (**attribute**) was (**summarizer**)."
  
where summarizer is a conclusive phrase for the summary (e.g., "high", "low", etc.), and quantifier is a word or phrase that specifies how often the summarizer is true (e.g., "most", "all", etc.), given an attribute of interest.  A concrete summary following the above protoform is: 

> “On **_most_ days** in the past **week**, your **sugar level** was **very high**.”

Our system relies on SAX representations of time-series data [1,3] and temporal/sequence pattern discovery via the SPADE algorithm [8]. SAX representations allow us to convert raw time-series data into symbolic strings containing letters of the alphabet. These representations make it easier for time-series analysis methods to find interesting patterns and anomalies efficiently in the data. Using the SPADE algorithm, we are able to discover frequent sequences, or patterns, in the data. These patterns are considered "frequent" if they are above the specified minimum support threshold, and summaries for these patterns are generated if they are above the specified minimum confidence threshold.

We mainly use data from the Insight4Wear dataset. Insight4Wear [2] is a quantified-self/life-logging app, with about 11.5 million records of information. It provides data gathered from mobile devices that tracks step counts, heart rates, and user activities from around 1,000 users.

## Implemented Protoforms

Below is a table of the current list of protoforms our system uses to generate summaries:

|     Summary Type      |   Protoform   |
|:---------------------:|:-------------:| 
| Standard Evaluation   | On Q sTW in the past TW, your A was S. | 
| Comparison            | You did S with G than you did the TW before.     |   
| Goal Evaluation       | On Q sTW in the past TW, you S the G.      |    
| Standard Trends       | Q time, your A S from one sTW to the next.     |  
| Cluster-based Pattern | During Q TW that follow this pattern, your A S the next TW.     |  
| If-then Pattern       | There is C confidence that, when your A is S1, then S2,...,then Sn, it tends to be Sn+1 the next TW.      | 

where S denotes a summarizer, Q is a quantifier, A is an attribute, G is a goal, C is a confidence value, TW is a time window, and sTW a sub-time window.


## Setup

This system was implemented in Python 2.7.

1. Install required Python packages using `pip install`
- numpy
- saxpy 
- squeezer
2. Set value of `attr_index` as index for the desired attribute (available attributes stored in `attributes` list)
3. Set `age`, `activity level`, `alpha_size` (alphabet size for SAX representation). and `tw` (time window size)
4. Set `min_conf` (minimum confidence) and `min_sup` (minimum support) thresholds
5. Set `path` to store pattern data for cSPADE
6. Set `cygwin_path` for path to Cygwin (or equivalent) to run C++ commands
7. Run `python proto.py` 

## Sample Run
<p align="center">
  <img src="https://github.com/harrij15/TemporalSummaries/blob/master/stepcountdata.png" height="350" weight="350"/>
</p>

The chart above is a snippet of step count data for one user in the Insight4Wear dataset that spans over 200 days. Using a time window of seven days and an alphabet size of 5, our system produces ten summaries using five different protoforms with a minimum confidence threshold of 50% and a minimum support threshold of 15%. Our approach generates a diverse set of summaries for the step count data, spanning standard evaluation summaries at the daily and the weekly granularities, comparison summaries, a goal evaluation summary, a standard trends summary, and if-then pattern summaries with 100% confidence.

These summaries are shown below:

|     Summary Type      |   Summary   |
|:---------------------:|:-------------:| 
| Standard Evaluation (weekly granularity)   | In the past week, your step count has been high. | 
| Standard Evaluation (daily granularity)  | Over more than half of the days in the past week, your step count has been moderate. | 
| Comparison            | You did better with keeping your step count high than you did the week before.     |   
| Comparison            | You did not do as well with keeping your step counts high than you did on the week starting on day 105.   |   
| Goal Evaluation       | On most of the days in the past weeks, you did not reach the American Heart Association’s recommended number of 10,000 steps per day.      |    
| Standard Trends       | More than half of the time, your step count increases from one day to the next.     |  
| If-then Pattern       | There is 100% confidence that, when your step count follows the pattern of being low, then low, it tends to be moderate the next day      |
| If-then Pattern       | There is 100% confidence that, when your step count follows the pattern of being low, then moderate, it tends to be very high the next day.      | 
| If-then Pattern       | There is 100% confidence that, when your step count follows the pattern of being high, then low, it tends to be low the next day.      | 
| If-then Pattern       | There is 100% confidence that, when your step count follows the pattern of being moderate, then very high, it tends to be low the next day.      | 


## References
1. Jessica Lin, Eamonn J. Keogh, Li Wei, and Stefano Lonardi. 2007. Experiencing SAX: A Novel Symbolic Representation of Time Series. Data Min. Knowl. Discov. 15 (08 2007), 107-144
2. Reza Rawassizadeh, Elaheh Momeni, Chelsea Dobbins, Joobin Gharibshah, and Michael Pazzani. 2016. Scalable Daily Human Behavioral Pattern Mining from Multivariate Temporal Data. IEEE Transactions on Knowledge and Data Engineering 28, 11 (Nov. 2016), 3098–3112.
3. Senin, P., Lin, J., Wang, X., Oates, T., Gandhi, S., Boedihardjo, A.P., Chen, C., Frankenstein, S., Lerner, M., GrammarViz 2.0: a tool for grammar-based pattern discovery in time series, ECML/PKDD Conference, 2014.
4. Ronald R. Yager. 1982. A new approach to the summarization of data. Information Sciences 28, 1 (1982), 69 – 86.
5.	Lotfi A. Zadeh. 1975. The concept of a linguistic variable and its application to approximate reasoning–I. Information Sciences 8, 3 (1975), 199 – 249.
6.	Lotfi A. Zadeh. 1983. A computational approach to fuzzy quantifiers in natural languages. Computers & Mathematics with Applications 9, 1 (1983), 149 – 184.
7.	Lotfi A. Zadeh. 2002. A prototype-centered approach to adding deduction capability to search engines-the concept of protoform. In International IEEE Symposium on Intelligent Systems.
8.	Mohammed J. Zaki. 2001. SPADE: An Efficient Algorithm for Mining Frequent Sequences. Machine Learning 42, 1 (01 Jan 2001), 31-60.
