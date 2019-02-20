# Temporal Summaries

## Framework

Our framework automatically generates a diverse set of natural language summaries of time-series data, where the linguistic structure of the summaries conform to a set of protoforms. A protoform is a template that can be used to generate a natural language statement once it is filled in with the necessary information. As an example, a simple protoform is:

> On (**quantifier**) (**sub-time window**) in the past (**time window**), your (**attribute**) was (**summarizer**).
  
where summarizer is a conclusive phrase for the summary (e.g., "high", "low", etc.), and quantifier is a word or phrase that specifies how often the summarizer is true (e.g., "most", "all", etc.), given an attribute of interest.  A concrete summary following the above protoform is: 

> “On **_most_ days** in the past **week**, your **sugar level** was **very high**.”

Our system relies on SAX representations of time-series data and temporal/sequence pattern discovery via the SPADE algorithm. SAX representations allow us to convert raw time-series data into symbolic strings containing letters of the alphabet. These representations make it easier for time-series analysis methods to find interesting patterns and anomalies efficiently in the data. Using the SPADE algorithm, we are able to discover frequent sequences, or patterns, in the data. These patterns are considered "frequent" if they are above the specified minimum support threshold, and summaries for these patterns are generated if they are above the specified minimum confidence threshold.

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
1. Set value of `attr_index` as index for the desired attribute (available attributes stored in `attributes` list)
2. Set `min_conf` (minimum confidence) and `min_sup` (minimum support) thresholds
3. Set `path` to store pattern data for cSPADE
4. Set `cygwin_path` for path to Cygwin (or equivalent) to run C++ commands
5. Run `python proto.py` 

## Example Run
![](https://github.com/harrij15/TemporalSummaries/blob/master/stepcountdata.png)

## References
