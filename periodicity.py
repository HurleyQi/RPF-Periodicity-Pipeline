import ribopy
import multiprocessing
import threading
import time
import numpy as np
import pandas as pd
import os
import json
import sys


def periodicity_per_transcript(coverage):
    """
    Get the periodicty count for the three nucleotide position for a transcript

    Parameters
    ----------
    coverage
        ribo_object coverage data for a transcript

    Returns
    -------
    result (array)
        type is integer, length is 3
    """
    result = [0,0,0]
    # uses numpy
    result[0] = int(np.sum(coverage[::3]))
    result[1] = int(np.sum(coverage[1::3]))
    result[2] = int(np.sum(coverage[2::3]))
    return result;



# get the total periodicity for a study
def get_periodicity(study, dynamic_range, start_and_stop, result_dict, lock):
    """
    Calculate the total periodicity for a study; saves the result into result_dict

    Parameters
    ----------
    study (str)
        The name of the study, ex. "GSExxxxxx"
    dynamic_range (manager.dict)
        Contains the dynamic range, read lengths with the highest read counts for each sample
    start_and_stop (manager.dict)
        Contains the start and stop site for each gene's CDS region
    result_dict (manager.dict)
        The periodicity result
    lock (manager.Lock)
        Global lock used to prevent possible race conditions
    """
    # set up file path
    study_path = os.path.join(os.getcwd(), "ribobase/"+study+"/ribo/experiments")

    # Check if ribo files exits and filter out non-ribo files 
    try: 
        files = os.listdir(study_path)
    except FileNotFoundError as e:
        print(f"Error: The study '{study}' does not have the expected directory")
        return None
    except Exception as e: 
        print(f"Error: The study '{study}' encountered an error in trying to access ribo files")
        return None

    ribo_files = [file for file in files if file.endswith(".ribo")]
    if not ribo_files:
        print(f" Error: No ribo files found in {study}")
        return None

    if not any(ribo_file[:-5] in dynamic_range for ribo_file in ribo_files):
        return None

    result = dict()
    for ribo_file in ribo_files:
        exp_path = os.path.join(study_path, ribo_file)
        exp_name = ribo_file[:-5]

        # determine human or mouse
        if ribo_file[:-5] in dynamic_range:
            start_length = dynamic_range[exp_name][0]
            stop_length = dynamic_range[exp_name][1] 
            study_start_and_stop = start_and_stop
        else:
            # print(f"Error: The ribo rile ({exp_name}, {study}) is not in dynamic range")
            continue

        result[exp_name] = dict()
        for read_length in range(start_length, stop_length + 1):
            read_length_periodicity = [0,0,0]
            # create ribo object and get coverage data for the curr read length, human ribo files
            # can use its alias for simplicity
            # human
            # curr_coverage = ribopy.Ribo(exp_path, ribopy.api.alias.apris_human_alias).get_coverage(
            #     experiment=exp_name,
            #     alias=True,
            #     range_lower=read_length,
            #     range_upper=read_length
            # )
            # # mouse
            curr_coverage = ribopy.Ribo(exp_path, alias=None).get_coverage(
                experiment=exp_name,
                alias=False,
                range_lower=read_length,
                range_upper=read_length
            )
            # iterate through the transcripts to sum up the read counts
            for transcript in curr_coverage.keys():
                cds_coverage = curr_coverage[transcript][study_start_and_stop[transcript][0]:study_start_and_stop[transcript][1]]
                if sum(cds_coverage) != 0 and cds_coverage.size % 3 == 0:
                    count_per_transcript = periodicity_per_transcript(cds_coverage)
                    read_length_periodicity = [x + y for x, y in zip(read_length_periodicity, count_per_transcript)]
            
            result[exp_name][read_length] = read_length_periodicity
    with lock: # lock may not be needed, but just for safety
        result_dict[study] = result
        # with open("./result/human_failed_periodicity.json", 'w') as json_f: 
        #     temp_final_result = dict(result_dict)
        #     json.dump(temp_final_result, json_f, indent=4)



def convert_to_managed_dict(data, manager):
    """
    Convert a regular dictionary to a multiprocessing.managers.DictProxy

    Parameters
    ----------
    data (dict)
        Regular dictionary to be converted to a Manager.dict
    manager (manager.Manager)
        Manager created in main to create a Manager.dict
    """
    if isinstance(data, dict):
        managed_dict = manager.dict()
        for key, value in data.items():
            managed_dict[key] = convert_to_managed_dict(value, manager)
        return managed_dict
    else:
        return data



def convert_to_regular_dict(manager_dict):
    """
    Convert a Manager.dict to a regular dictionary

    Parameters
    ----------
    manager_dict (Manager.dict)
        Manager.dict to be converted to a regular dictionary
    """
    regular_dict = dict()
    for key, value in manager_dict.items():
        if isinstance(value, multiprocessing.managers.DictProxy):
            regular_dict[key] = convert_to_regular_dict(value)
        else:
            regular_dict[key] = value
    return regular_dict



### Main

# ensures this is only ran once
if __name__ == "__main__":
    # creating/opening global dictionaries for dynamic range and start and stop sites
    main_manager = multiprocessing.Manager()
    manager_lock = main_manager.Lock()
    species_list = ["human", "mouse"]
    QC_results = ["_passed_", "_failed_"]

    for species in species_list:
        for QC in QC_results: 
            print(species, QC)
            output_file_path = f"./result/{species}{QC}periodicity.json"
            
            # loading in dynamic range
            dynamic_range_dir = os.path.join(os.getcwd(), "dynamic_range")
            with open(os.path.join(dynamic_range_dir, species+QC+"dynamic_range.json"), 'r') as j_file:
                dynamic_range = json.load(j_file)  

            # loading in start and stop sites
            start_stop_dir = os.path.join(os.getcwd(), "start_stop_sites")
            with open(os.path.join(start_stop_dir, species+"_start_stop.json"), 'r') as j_file:
                start_stop = json.load(j_file)

            studies_list_path = os.path.join(os.getcwd(), "studies_lists")
            with open(os.path.join(studies_list_path, "studies.json"), 'r') as j_file:
                studies_lists = json.load(j_file)
            
            # Create shared dictionaries
            manager_dynamic_range = main_manager.dict()
            manager_start_and_stop = main_manager.dict()

            # converting to manager.dict() so they are shared between all processes
            # saves memory and faster performance
            manager_dynamic_range = convert_to_managed_dict(dynamic_range, main_manager)
            manager_start_and_stop = convert_to_managed_dict(start_stop, main_manager)

        ## used for running on TACC

            if os.path.exists(output_file_path):
                with open(output_file_path, 'r') as j_file: 
                    saved_result = json.load(j_file)
                manager_result = convert_to_managed_dict(saved_result, main_manager)
            else:
                manager_result = main_manager.dict()

            processes = []

            curr_studies_lists = studies_lists[species+QC]
            # # # generate a process to calculate periodicity for each study
            try:
                for study in curr_studies_lists: 
                    if study not in manager_result:
                        p = multiprocessing.Process(
                            target=get_periodicity,
                            args=(
                                study, 
                                manager_dynamic_range, 
                                manager_start_and_stop, 
                                manager_result, 
                                manager_lock
                            ), 
                            name=study
                        )
                        processes.append(p)
                        p.start()
            except Exception as e:
                print(f'Error: Creating processes encountered this error: {e}')
                # Terminate processes
                for p in processes:
                    if p.is_alive():
                        p.terminate()
                        p.join()
                sys.exit(1)    

            # waiting for every process to finish
            for p in processes:
                p.join()
            
            # save final result
            final_result = convert_to_regular_dict(manager_result)
            with open(output_file_path, 'w') as json_f: 
                json.dump(final_result, json_f, indent=4)



    main_manager.shutdown()

