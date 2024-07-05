import pandas as pd
import json

"""
This script parses the given `dynamic_range.xlsx` to obtain the dynamic range, a range of 
read length where its read counts are the highest, for each samples. The script parses the 
xlsx file for human and mouse and further separates the result into QC_passed and QC_failed. 
The results are stored in a dict and saved as .json files

Result format
-------------
{
    "sample_name" (str): [start_length, stop_length] (int array) 
}
"""

## get human dynamic range

# human_df = pd.read_excel("./dynamic_range/dynamic_range.xlsx", sheet_name="human")

# passed_result = dict()
# failed_result = dict()

# for index, row in human_df.iterrows():
#     if row.iloc[6] == "keep":
#         passed_result[row.iloc[0]] = ( row.iloc[2], row.iloc[3] )
#     else:
#         failed_result[row.iloc[0]] = ( row.iloc[2], row.iloc[3] )

# with open("./dynamic_range/human_passed_dynamic_range.json", "w") as j_file: 
#     json.dump(passed_result, j_file, indent=4)

# with open("./dynamic_range/human_failed_dynamic_range.json", "w") as j_file: 
#     json.dump(failed_result, j_file, indent=4)



## get human dynamic range

mouse_df = pd.read_excel("./dynamic_range/dynamic_range.xlsx", sheet_name="mouse")

passed_result = dict()
failed_result = dict()

for index, row in mouse_df.iterrows():
    if row.iloc[6] == "Pass":
        passed_result[row.iloc[0]] = ( row.iloc[2], row.iloc[3] )
    else:
        failed_result[row.iloc[0]] = ( row.iloc[2], row.iloc[3] )


with open("./dynamic_range/mouse_passed_dynamic_range.json", "w") as j_file: 
    json.dump(passed_result, j_file, indent=4)

with open("./dynamic_range/mouse_failed_dynamic_range.json", "w") as j_file: 
    json.dump(failed_result, j_file, indent=4)