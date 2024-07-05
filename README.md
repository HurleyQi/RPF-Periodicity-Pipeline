# Periodicity Check

This repository contains code supporting the manuscript titled 'xxxx'. The scripts within the repository parses the `dynamic_range.xlsx` for dynamic ranges for each sample, 
parses the transcriptome for start and stop site of CDS region for each genes, parses the RiboBase to separate the studies based on species and QC statues, processes and graphs
the resulting periodicity for all samples. 

## Overview 

* `.\dynamic_range` - Contains `dynamic_range.xlsx` and the subsequent parsed dynamic ranges for different species and QC status and the script for parsing.  
* `.\result` - Contains the periodicity result, saved as .json files, for each species and QC status
* `.\start_stop_sites` - Contains the transcriptomes and subsequence start and stop sites of the CDS for each genes, and the script for parsing. 
* `.\studies_lists` - Contains the list of studies for each species and QC status and the script for parsing. 
* `.\study_level_graphs` - Contains the resulting pdf graphs for study level plots. 

## Result structure

The periodicity results are stored as dictionaries and saves as .json files. The results all follow a specific structure that as listed out below. 

```
{
  "study_name" (str) ex. "GSExxxxx" : {
    "sample_name" (str) ex. "GSMxxxxx" : {
      "read_length" (str) ex. "25" : [x, x, x] # array of three ints that stores the periodicity count
    }
  }
}
```

## Getting started

### Files you need to calculate TE
Ribo files required to reproduce these results are not included in the repo for size reasons and need to be requested by email ccenik@austin.utexas.edu, or generated yourself via scripts under riboflow_scr.

### Work Flow
To calculate the periodicity, first you need to generate the corresponding start_stop_sites, studies_list, dynamic_range using the provided scripts in each separate subdirectories, or use the provided version stored. 
To calculate periodicity, simply run `periodicity.py`, and the graph the results, use `graph_periodicity.py`. 

## Contact
If you have any questions, please email hurleyqi@utexas.edu or yliu5@utexas.edu.
