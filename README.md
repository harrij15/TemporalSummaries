# Temporal Summaries

## Defined Terms

- Protoform (P): A sentence prototype (or template) that can be used to generate a natural language summary once it is filled in with the necessary information
- Summarizer (S): A conclusive phrase for the summary
- Quantifier (Q): A word or phrase that specifies how often the summarizer is true, given the object of interest
- Attribute (A): A variable of interest in the database
- Time window (TW): A time window of interest
- Sub-time window (sTW): A time window at a smaller granularity than the specified time window
- Qualifier (R): A word or phrase that adds specificity to the summary

## Framework

Our framework automatically generates a diverse set of natural language summaries of time-series data, where the linguistic structure of the summaries conform to a set of protoforms. A protoform is a template that can be used to generate a natural language statement once it is filled in with the necessary information [4,5,6,7]. As an example, a simple protoform is:

> "On (**quantifier**) (**sub-time window**) in the past (**time window**), your (**attribute**) was (**summarizer**)."
  
where summarizer is a conclusive phrase for the summary (e.g., "high", "low", etc.), and quantifier is a word or phrase that specifies how often the summarizer is true (e.g., "most", "all", etc.), given an attribute of interest.  A concrete summary following the above protoform is: 

> “On **_most_ days** in the past **week**, your **sugar level** was **very high**.”

Our system relies on SAX representations of time-series data [1,3] and temporal/sequence pattern discovery via the SPADE algorithm [8]. SAX representations allow us to convert raw time-series data into symbolic strings containing letters of the alphabet. These representations make it easier for time-series analysis methods to find interesting patterns and anomalies efficiently in the data. Using the SPADE algorithm, we are able to discover frequent sequences, or patterns, in the data. These patterns are considered "frequent" if they are above the specified minimum support threshold, and summaries for these patterns are generated if they are above the specified minimum confidence threshold.

We provide sample data from the Alpha Vantage REST API and the National Centers For
Environmental Information (NCEI). Alpha Vantage [2] provides free APIs that allow users to receive real-time and historical financial data. NCEI [9] provides average temperature and average wind speed data tracked at the daily and hourly granularity by the weather station at the Huntsville International Airport in Huntsville, Alabama. 

We are unable to provide data for the running example but this can be accessed by following this link: https://larc.smu.edu.sg/myfitnesspal-food-diary-dataset.

## Implemented Protoforms

Below is a table of the current list of protoforms our system uses to generate summaries:

|     Summary Type      |   Protoform   |
|:---------------------:|:-------------:| 
| Standard Evaluation (TW)  | In the past full TW, your A<sub>1</sub> has been S<sub>1</sub>,..., and your A<sub>n</sub> has been S<sub>n</sub>. | 
| Standard Evaluation (sTW)   | On Q sTW in the past TW, your A<sub>1</sub> was S<sub>1</sub>,..., and your A<sub>n</sub> was S<sub>n</sub>. | 
| Standard Evaluation (sTW w/ qualifier)   | On Q sTW in the past TW R, your A<sub>1</sub> was S<sub>1</sub>,..., and your A<sub>n</sub> was S<sub>n</sub>. | 
| Comparison            | Your A<sub>1</sub> was S<sub>1</sub>,..., and your A<sub>n</sub> was S<sub>n</sub> on TW<sub>1</sub> N<sub>1</sub> than they were on TW<sub>2</sub> N<sub>2</sub>. |  
| Goal Comparison            | You did S<sub>1</sub> overall with keeping your A<sub>1</sub> G<sub>1</sub>,..., and you did S<sub>n</sub> overall with keeping your A<sub>n</sub> G<sub>n</sub> in TW<sub>1</sub> N<sub>1</sub> than you did in TW<sub>2</sub> N<sub>2</sub>. |   
| Goal Evaluation       | On Q sTW in the past TW, you S<sub>1</sub> your goal to keep your A<sub>1</sub> G<sub>1</sub>,..., and you S<sub>n</sub> your goal to keep your A<sub>n</sub> G<sub>n</sub>.      |    
| Standard Trends       | Q time, your A<sub>1</sub> S<sub>1</sub>,..., and your A<sub>n</sub> S<sub>n</sub> from one sTW to the next.     |  
| Cluster-Based Pattern | During Q TW similar to TW N, your A<sub>1</sub> S<sub>1</sub>,..., and your A<sub>n</sub> S<sub>n</sub> the next TW.     |  
| Standard Pattern | The last time you had a TW similar to TW N, your A<sub>1</sub> S<sub>1</sub>,..., and your A<sub>n</sub> S<sub>n</sub> the next TW.     |  
| If-Then Pattern       | There is C confidence that, when your A<sub>1</sub> is S<sub>11</sub>, then S<sub>21</sub>,..., then S<sub>m1</sub>,..., and your A<sub>n</sub> is S<sub>1n</sub>, then S<sub>2n</sub>,..., then S<sub>mn</sub>, your A<sub>1</sub> tends to be S<sub>(m+1)1</sub>,..., and your A<sub>n</sub> tends to be S<sub>(m+1)n</sub> the next TW.      | 
| Day If-Then Pattern       | There is C confidence that, when your A<sub>1</sub> is S<sub>11</sub> on a D<sub>11</sub>, then S<sub>21</sub> on a D<sub>21</sub>,..., then S<sub>m1</sub> on a D<sub>m1</sub>,..., and your A<sub>n</sub> is S<sub>1n</sub> on a D<sub>1n</sub>, then S<sub>2n</sub> on a D<sub>2n</sub>,..., then S<sub>mn</sub> on a D<sub>mn</sub>, your A<sub>1</sub> tends to be S<sub>(m+1)1</sub> on a D<sub>(m+1)1</sub>,..., and your A<sub>n</sub> tends to be S<sub>(m+1)n</sub> on a D<sub>(m+1)n</sub> the next TW.      | 
 | General If-Then Pattern       | In general, if your A<sub>1</sub> is S<sub>1</sub>,..., and your A<sub>n</sub> is S<sub>n</sub>, then your A<sub>n+1</sub> is S<sub>n+1</sub>,..., and your A<sub>n+m</sub> is S<sub>n+m</sub>.      | 
| Day-Based Pattern | Your A<sub>1</sub> tends to be S<sub>1</sub>,..., and your A<sub>n</sub> tends to be S<sub>n</sub> on D.     |  
| Goal Assistance | In order to better follow the G, you should S<sub>1</sub> your A<sub>1</sub>, S<sub>2</sub> your A<sub>2</sub>, ..., and S<sub>n</sub> your A<sub>n</sub>.     |  
| Population Evaluation | Q<sub>1</sub> users in this study had a S<sub>1</sub> A<sub>1</sub>, a S<sub>2</sub> A<sub>2</sub>, ..., and a S<sub>n</sub> A<sub>n</sub> P.     |  


where S denotes a summarizer, Q is a quantifier, R is a qualifier, A is an attribute, G is a goal, D is a day of the week, C is a confidence value, TW is a time window, sTW is a sub-time window, N is a time window index, and P is a sub-protoform.


## Setup

This system was implemented in Python 3.

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
  <img src="https://github.com/harrij15/TemporalSummaries/blob/master/stock_data.png" height="350" weight="350"/>
</p>

The chart above is a snippet of stock market ticker data for Apple and Aetna that spans 100 days. Using a time window of seven days and an alphabet size of 5, our system produces 287 summaries (both univariate and multivariate) using seven different protoforms with a minimum confidence threshold of 80% and a minimum support threshold of 20%. Our approach generates a diverse set of summaries for the ticker data.

A subset of multivariate summaries for Apple and Aetna are shown below. Please note that not all protoforms are appropriate for stock market ticker data.

|     Summary Type      |   Summary   |
|:---------------------:|:-------------:| 
| Standard Evaluation (weekly granularity)   | In the past full week, the AAPL close value has been very high and the AET close value has been very high. | 
| Standard Evaluation (daily granularity)  | On all of the days in the past week, the AAPL close value has been very high and the AET close value has been very high. | 
| Standard Evaluation (daily granularity w/ qualifier)  | On all of the days in the past week, when the AAPL close value was very high, the AET close value was very high. | 
| Comparison            |The AAPL close value was about the same and the AET close value was about the same in week 13 as they were in week 12.     |   
| Standard Trends       | Some of the time, the AAPL close value increases and the AET close value increases from one day to the next.     |  
| If-Then Pattern       | There is 100% confidence that, when your AAPL close value follows the pattern of being high, your AET close value tends to be high, then high the next day. |
| Day-Based Pattern       | The AAPL close value tends to be very high and the AET close value tends to be very high on Thursdays. |


## References
1. Jessica Lin, Eamonn J. Keogh, Li Wei, and Stefano Lonardi. 2007. Experiencing SAX: A Novel Symbolic Representation of Time Series. Data Min. Knowl. Discov. 15 (08 2007), 107-144
2. Romel Torres. 2019. Alpha Vantage. https://github.com/RomelTorres/alpha_vantage.
3. Senin, P., Lin, J., Wang, X., Oates, T., Gandhi, S., Boedihardjo, A.P., Chen, C., Frankenstein, S., Lerner, M., GrammarViz 2.0: a tool for grammar-based pattern discovery in time series, ECML/PKDD Conference, 2014.
4. Ronald R. Yager. 1982. A new approach to the summarization of data. Information Sciences 28, 1 (1982), 69 – 86.
5.	Lotfi A. Zadeh. 1975. The concept of a linguistic variable and its application to approximate reasoning–I. Information Sciences 8, 3 (1975), 199 – 249.
6.	Lotfi A. Zadeh. 1983. A computational approach to fuzzy quantifiers in natural languages. Computers & Mathematics with Applications 9, 1 (1983), 149 – 184.
7.	Lotfi A. Zadeh. 2002. A prototype-centered approach to adding deduction capability to search engines-the concept of protoform. In International IEEE Symposium on Intelligent Systems.
8.	Mohammed J. Zaki. 2001. SPADE: An Efficient Algorithm for Mining Frequent Sequences. Machine Learning 42, 1 (01 Jan 2001), 31-60.
9. Matthew J. Menne, Imke Durre, Bryant Korzeniewski, Shelley McNeal, Kristy Thomas, Xungang Yin, Steven Anthony, Ron Ray, Russell S.Vose, Byron E.Gleason, and Tamara G. Houston. 2020.   Global Historical Climatology Network - Daily (GHCN-Daily), Version 3. https://www.ncei.noaa.gov/.
