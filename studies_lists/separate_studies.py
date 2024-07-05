import os
import json


"""
This script uses the given `./dynamic_range/dynamic_range.xlsx` and traverses through the RiboBase
to separate studies into human and mouse along with their QC status. The result is stored in a
dict and saved as a .json file. 

Result format
-------------
{
    "species_QC" (str): [study_names] (str array) 
}
"""


species = ["human", "mouse"]
QC_results = ["_passed_", "_failed_"]
studies = os.listdir("./ribobase")

result = dict()

for item in species:
    for QC in QC_results: 
        studies_list = []
        # loading in dynamic range
        dynamic_range_dir = os.path.join(os.getcwd(), "dynamic_range")
        with open(os.path.join(dynamic_range_dir, item+QC+"dynamic_range.json"), 'r') as j_file:
            dynamic_range = json.load(j_file)  

        for study in studies: 
            if study.startswith("GSE") and study.endswith("_dedup"):
                study_path = os.path.join(os.getcwd(), "ribobase/"+study+"/ribo/experiments")

                try: 
                    files = os.listdir(study_path)
                except Exception as e: 
                    print(f"Error: The study '{study}' encountered an error in trying to access ribo files")
                    continue

                ribo_files = [file for file in files if file.endswith(".ribo")]
                if not ribo_files:
                    print(f" Error: No ribo files found in {study}")
                    continue

                if any(ribo_file[:-5] in dynamic_range for ribo_file in ribo_files):
                    studies_list.append(study)
                
        result[item+QC] = studies_list

with open("./studies_lists/studies.json", 'w') as j_file: 
    json.dump(result, j_file, indent=4)