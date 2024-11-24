# Periodicity Check

This repository contains code supporting the periodicity analysis presented in 
the paper titled "Translation efficiency covariation across cell types is a conserved 
organizing principle of mammalian transcriptomes." The latest 
[preprint](https://www.biorxiv.org/content/10.1101/2024.08.11.607360v1) 
is available on bioRxiv.


## Overview 

Three-nucleotide periodicity is a unique feature of ribosome profiling data. 
It is a bias in the mapped read counts towards one of the three reading frames [1]. 
This bias is influenced by P-site offsets and may not always be on the first nucleotide.

Each ribosome profiling sample in RiboBase has its own dynamic range of read lengths, ensuring 
optimized coverage for further analysis [2]. This repository provides scripts to:
* Retrieve dynamic read-length ranges for each sample
* Parse the transcriptome to identify the start and stop sites of coding sequences (CDS) for each gene
* Calculate periodicity for all samples in RiboBase

Here is an overview of the structure of the codebase:

* `.\dynamic_range` - Contains the script to retrieve the dynamic ranges for different species and its QC status
* `.\result` - Location to store the results
* `.\start_stop_sites` - Contains the script to parse the transcriptomes for the start and stop sites of the CDS for each genes
* `.\studies_lists` - Contains  the script to parse the list of studies and its QC status

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
Ribo files required to reproduce these results are not included in the repo for size reasons and need to be requested by email ccenik@austin.utexas.edu.

### Work Flow
To calculate the periodicity, first you need to generate the corresponding start_stop_sites, studies_list, dynamic_range using the provided scripts in each separate subdirectories. 
To calculate periodicity, simply run `periodicity.py`, and the graph the results, use `graph_periodicity.py`. 

## Contact
If you have any questions, please email hurleyqi@utexas.edu

## References
[1] Liu, Y., Hoskins, I., Geng, M., Zhao, Q., Chacko, J., Qi, K., ... & Cenik, C. (2024). Translation efficiency covariation across cell types is a conserved organizing principle of mammalian transcriptomes. bioRxiv.

[2] Douka, K., Agapiou, M., Birds, I., & Aspden, J. L. (2022). Optimization of ribosome footprinting conditions for Ribo-Seq in human and Drosophila melanogaster tissue culture cells. Frontiers in Molecular Biosciences, 8, 791455.
