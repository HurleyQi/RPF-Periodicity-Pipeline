import json
import os

"""
This script parses the transcriptome for human and mouse to obtain the start and stop site of the 
CDS region for each gene. The human transcriptome uses the alias version for simplicity when 
creating ribo_objects. The results are stored in a dict and saved as .json files

Result format
-------------
{
    "gene_name" (str): [start_site, stop_site] (int array) 
}
"""

curr_dir = os.path.join(os.getcwd(), "start_stop_sites")

result = dict()
with open(os.path.join(curr_dir, "appris_mouse_v2_actual_regions.bed.txt")) as file: 
    for line in file: 
        split_line = line.split()
        if "CDS" in split_line: 
            result[split_line[0]] = ( int(split_line[1]), int(split_line[2]) )

with open(os.path.join(curr_dir, "mouse_start_stop.json"), "w") as j_file:
    json.dump(result, j_file, indent=4)