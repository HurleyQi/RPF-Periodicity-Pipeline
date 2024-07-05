import matplotlib.pyplot as plt
import json
import numpy as np
import itertools
import os 


### fonts to use for plotting
titlefont = {'fontname': 'Times'}
labelfont = {'fontname': 'serif'}



def normalize_array(arr):
    """
    Normalize a periodicity array such that the sum of all elements add up to 1

    Parameters
    ----------
    arr (array)
        Periodicity array to be normalized 
    """
    total_sum = sum(arr)
    if total_sum == 0:
        return arr  # Avoid division by zero
    normalized_arr = [float(x) / total_sum for x in arr]
    return normalized_arr



def get_periodicity_study_level(data, threshold):
    """
    Obtains the periodicty data from ./result for graphing periodicity at the study level. 
    Returns the aggregated periodicity for all the studies and a tuple consisting of the 
    pattern separation indexes 

    Parameters
    ----------
    data (dict)
        Dictionary that is loaded from the json file in result, contains the periodicty data
        in the specific form as stated in the README.md
    threshold (float)
        Threshold value which used to separate the periodicty result into different patterns
    """
    # separating the periodicity into three patterns (mentioned in methods)
    periodicty_data = [[], [], []] 
    studies_list = list(data.keys())
    for study in studies_list:
        study_dict = dict()
        curr_study = data[study]
        # aggregating the periodicity counts by study according to the read length 
        for sample_dict in curr_study.values():
            for read_length, periodicty in sample_dict.items():
                # reordering the read counts from highest to lowest at the sample level 
                periodicty = sorted(periodicty, reverse=True)
                if read_length in study_dict.keys():
                    study_dict[read_length] = [x + y for x, y in zip(study_dict[read_length], periodicty)]
                else:
                    study_dict[read_length] = periodicty

        # find the read length with the max read counts for a study
        max_read_length = max(study_dict, key=lambda k: sum(study_dict[k]))
        max_periodicity = normalize_array(study_dict[max(study_dict, key=lambda k: sum(study_dict[k]))])
        study_name = study.replace("_dedup", "")[:3] + '\n' + study.replace("_dedup", "")[3:]

        # seperate the current study's maximum read length's periodicity into one of the three
        # patterns 
        if max_periodicity[1] * threshold <= max_periodicity[0]:
            periodicty_data[0].append( ( max_periodicity, (study_name , max_read_length ) ) )
        elif max_periodicity[2] * threshold <= max_periodicity[0] and \
            int(max_periodicity[2] * threshold) <= max_periodicity[1]:
            periodicty_data[1].append( ( max_periodicity, (study_name, max_read_length ) ) )
        else:
            periodicty_data[2].append( ( max_periodicity, (study_name, max_read_length ) ) )
    
    separation_index = (len(periodicty_data[0]), len(periodicty_data[0]) + len(periodicty_data[1]))
    result = list(itertools.chain(*periodicty_data))

    return (result, separation_index) #return the aggregated periodicity and separation indexes



def graph_periodicity_study_level(data, num_cols, threshold, supertitle):
    """
    Graphs the periodicty data from ./result at the study level.
    Saves the result, which has the bar plot for each study's max read length, as a pdf. 

    Parameters
    ----------
    data (dict)
        Dictionary that is loaded from the json file in result, contains the periodicty data
        in the specific form as stated in the README.md
    num_cols (int)
        Number of columns in the final pdf
    threshold (int/float)
        Threshold value which used to separate the periodicty result into different patterns 
    supertitle (str)
        Title of the entire pdf graph
    """
    # gets the periodicty value and separation index needed for plotting
    periodicty_data, separation_index = get_periodicity_study_level(data, threshold)
    first_type, second_type = separation_index[0], separation_index[1]

    # Ceil division to get the number of rows needed
    num_rows = (len(data.keys()) + num_cols - 1) // num_cols  
    
    # generate the plot and its subplots, final pdf size is 7 x 10 inches
    fig, axes = plt.subplots(num_rows, 1, figsize=(7, 10))

    # special case of only one row
    if num_rows == 1:
        axes = [axes]  

    title_y_position = 0.9 # varies depends on the number of studies 
    for row in range(num_rows):
        ax = axes[row]
        x_ticks = []
        x_labels = []
        for col in range(num_cols):
            study_index = row * num_cols + col
            # separate the three patterns into different colors
            if study_index < first_type:
                color = "green"
            elif study_index < second_type:
                color = "blue"
            else:
                color = "red"

            if study_index < len(data.keys()):
                x = np.arange(3) + col * (3 + 1)
                ax.bar(x, periodicty_data[study_index][0], color=color)
                ax.text(
                    x.mean(), 
                    title_y_position, 
                    periodicty_data[study_index][1][0], 
                    ha='center', 
                    va='bottom', 
                    fontsize=6.5, 
                    **titlefont
                )
                x_ticks.append(x.mean())
                x_labels.append(periodicty_data[study_index][1][1])
            else: # add dummy bars to maintain format
                x = np.arange(3) + col * (3 + 1)
                ax.bar(x, [0, 0, 0], color='white') 

        ax.set_ylim(0, 1.1) 
        ax.set_xticks(x_ticks, x_labels, fontsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.subplots_adjust(top=0.98)
    fig.suptitle(supertitle, fontsize=11.5, **titlefont, y=1.001)

    # saves the final image
    plt.savefig(f"{supertitle}.pdf", format='pdf', dpi=600)
    plt.show()



def get_periodicity_sample_level(data, threshold):
    """
    Obtains the periodicty data from ./result for graphing periodicity at the sample level. 
    Returns the aggregated periodicity for all the samples 

    Parameters
    ----------
    data (dict)
        Dictionary that is loaded from the json file in result, contains the periodicty data
        in the specific form as stated in the README.md
    threshold (float)
        Threshold value which used to separate the periodicty result into different patterns
    """
    # specific form of the resulting data structure that stores the periodicity data
    result = {
        "pattern_one":{
            "sum":0,
            "periodicty_count":np.array([0, 0, 0])
        },
        "pattern_two":{
            "sum":0,
            "periodicty_count":np.array([0, 0, 0])
        },
        "pattern_three":{
            "sum":0,
            "periodicty_count":np.array([0, 0, 0])
        }
    }
    for study_name in data.keys():
        for sample_dict in data[study_name].values():
            # find the read length that has the max read counts and its periodicity
            max_periodicity = [0, 0, 0]
            for read_length, periodicty in sample_dict.items():
                if sum(periodicty) > sum(max_periodicity):
                    max_periodicity = sorted(periodicty, reverse=True)

            # separate into three patterns
            if int(max_periodicity[1] * threshold) <= max_periodicity[0]:
                result["pattern_one"]["sum"] += 1
                result["pattern_one"]["periodicty_count"] = np.add(
                    np.array(max_periodicity), 
                    result["pattern_one"]["periodicty_count"]
                )
            elif int(max_periodicity[2] * threshold) <= max_periodicity[0] and \
                int(max_periodicity[2] * threshold) <= max_periodicity[1]:
                result["pattern_two"]["sum"] += 1
                result["pattern_two"]["periodicty_count"] = np.add(
                    np.array(max_periodicity), 
                    result["pattern_two"]["periodicty_count"]
                )
            else:
                result["pattern_three"]["sum"] += 1
                result["pattern_three"]["periodicty_count"] = np.add(
                    np.array(max_periodicity), 
                    result["pattern_three"]["periodicty_count"]
                )
    return result



def graph_periodicity_sample_level(species_list, QC_results, threshold):
    """
    Graphs the periodicty data from ./result at the sample level.
    Saves the result, which separates all sample's periodicity into three patterns, as a pdf. 

    Parameters
    ----------
    species_list (array (str))
        Array of the species within the RiboBase
    QC_results (array (str))
        Array of the quality control statues of the samples
    threshold (int/float)
        Threshold value which used to separate the periodicty result into different patterns 
    """
    # generate the plot and its subplots, final pdf size is 5 x 8 inches
    fig, axes = plt.subplots(4, 1, figsize=(5, 8))

    row_index = 0
    title_y_position = 0.9
    # iterate through all possible species and QC combinations 
    for species in species_list:
        for QC in QC_results: 
            curr_data_path = f"./result/{species}{QC}periodicity.json"
            with open(curr_data_path) as j_file: 
                data = json.load(j_file)
            # get the periodicity date for the current species and QC status
            curr_periodicity = get_periodicity_sample_level(data, threshold)
            # normalize the data
            for pattern in curr_periodicity.values():
                pattern["periodicty_count"] = normalize_array(pattern["periodicty_count"])

            ax = axes[row_index]

            # sets the title for the subplot row
            QC = QC.replace("_", "")
            ax.set_title(f"{species} QC {QC}", **titlefont)

            # graphs the bar plot for the three patterns 
            x = np.arange(3) + 0 * (3 + 1)
            ax.bar(x, curr_periodicity["pattern_one"]["periodicty_count"], color="green")
            ax.text(
                x.mean(), 
                title_y_position, 
                str(curr_periodicity["pattern_one"]["sum"]), 
                ha='center', 
                va='bottom', 
                fontsize=12, 
                **titlefont
            )
 
            x = np.arange(3) + 1 * (3 + 1)
            ax.bar(x, curr_periodicity["pattern_two"]["periodicty_count"], color="blue")  
            ax.text(
                x.mean(), 
                title_y_position, 
                curr_periodicity["pattern_two"]["sum"], 
                ha='center', 
                va='bottom', 
                fontsize=12, 
                **titlefont
            )

            x = np.arange(3) + 2 * (3 + 1)
            ax.bar(x, curr_periodicity["pattern_three"]["periodicty_count"], color="red") 
            ax.text(
                x.mean(), 
                title_y_position, 
                curr_periodicity["pattern_three"]["sum"], 
                ha='center', 
                va='bottom', 
                fontsize=12, 
                **titlefont
            )

            row_index += 1

            ax.set_ylim(0, 1.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_xticks([])

    fig.suptitle("Periodicity Check", fontsize=14, **titlefont)
    # Adjust layout
    plt.tight_layout()
    plt.savefig('periodicity_sample_level.pdf', format='pdf', dpi=600)
    plt.show()



### main

species_list = ["human", "mouse"]
QC_results = ["_passed_", "_failed_"]

## study level

# need to alter font size for better display results
for species in species_list:
    for QC in QC_results: 
        title = species+QC+"studies_periodicity"
        curr_data_path = f"./result/{species}{QC}periodicity.json"
        with open(curr_data_path) as j_file: 
            data = json.load(j_file)

        graph_periodicity_study_level(data, 15, 2, title)


## sample level 

# graph_periodicity_sample_level(species_list, QC_results, 2)
