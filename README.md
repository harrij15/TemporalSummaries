# Temporal Summaries

## System

Our framework automatically generates a diverse set of natural language summaries of time-series data, where the linguistic structure of the summaries conform to a set of protoforms. A protoform is a template that can be used to generate a natural language statement once it is filled in with the necessary information. As an example, a simple protoform is:

On (quantifier) (sub-time window) in the past (time window), your (attribute) was (summarizer).
  
where summarizer is a conclusive phrase for the summary (e.g., "high", "low", etc.), and quantifier is a word or phrase that specifies how often the summarizer is true (e.g., "most", "all", etc.), given an attribute of interest.  A concrete summary following the above protoform is: “On **_most_ days** in the past **week**, your **sugar level** was **very high**.”

Our system relies on SAX representations of time-series data and temporal/sequence pattern discovery via the SPADE algorithm. SAX representations allow us to convert raw time-series data into symbolic strings containing letters of the alphabet. These representations make it easier for time-series analysis methods to find interesting patterns and anomalies efficiently in the data. Using the SPADE algorithm, we are able to discover frequent sequences, or patterns, in the data. 

## System Requirements

## References
