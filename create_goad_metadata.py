import zipfile
import pandas as pd
import os
import pdb

ext_drive_path = '/Volumes/VERBATIM HD'
collection = 'goad'

ssheet_path = f'./xlsxs/{collection}.xlsx'
metadata_path = f'./metadata/{collection}/'
metadata_groups_path = f'./metadata/{collection}/metadata_groups/'
geotiff_path = f'{ext_drive_path}/georef_geotiffs/{collection}/'
zip_path = f'{ext_drive_path}/repo_zip_groups/{collection}/'

if not os.path.isdir(zip_path):
    os.makedirs(zip_path)
if not os.path.isdir(metadata_groups_path):
    os.makedirs(metadata_groups_path)

# Read the Excel file into a DataFrame
df = pd.read_excel(ssheet_path)
df = df.sort_values(by='title')

def get_file_size(id):
    geotiff_file_path = geotiff_path + id + '.tif'
    if os.path.exists(geotiff_file_path):
        return os.stat(geotiff_file_path).st_size / (1024 * 1024)
    else:
        return 0

df['file_size_mb'] = df['id'].apply(get_file_size)
df['zip_group'] = ''

# Contains dfs which each are all of city_group
split_dfs = {}

for city_group in df['city_group'].unique():
    split_dfs[city_group] = df[df['city_group'] == city_group]

# If changing threshold also update threshold reset below
threshold = 1000 # mb
splits = []
current_split = []

# This will contain all dfs to create zip package csvs of right size in mb
split_city_group_split_dfs = {}

for city_group, df_split in split_dfs.items():
    df_split['cumulative_sum'] = df_split['file_size_mb'].cumsum()

    # Iterate through rows to split the DataFrame
    for index, row in df_split.iterrows():
        current_split.append(row)
        if row['cumulative_sum'] >= threshold:
            splits.append(pd.DataFrame(current_split))
            threshold += threshold
            current_split = []

    # Handle any remaining data in the last split
    if current_split:
        splits.append(pd.DataFrame(current_split))

    # All city groups will be added to split_city_group_split_dfs with a number suffix
    if len(splits) > 0:
        for i, s_df in enumerate(splits):
            city_group_num = str(i + 1)
            split_city_group_split_dfs[city_group + ' zip' + city_group_num] = s_df

    # Reset all for next city group
    splits = []
    current_split = []
    # If changing threshold also update threshold reset above
    threshold = 1000

# for city_group, df_split in split_city_group_split_dfs.items():
#     filename = f"./metadata/goad/split_city_group_split_dfs/{city_group}_{collection}.csv"
#     df_split.to_csv(filename, index=False)

# Update dataframe column with new city_groups for metadata export
for city_group_i, df_split_i in split_city_group_split_dfs.items():
    print(city_group_i)
    for index, row in split_city_group_split_dfs[city_group_i].iterrows():
        df.loc[df['id'] == row['id'], 'zip_group'] = city_group_i
        df_split_i.loc[df['id'] == row['id'], 'zip_group'] = city_group_i

# Save each split DataFrame as a separate CSV file
for city_group, df_split in split_city_group_split_dfs.items():
    df_split = df_split.drop(columns=['cumulative_sum'])
    filename = f"{metadata_groups_path}{city_group}_{collection}.csv"
    df_split.to_csv(filename, index=False)

df.to_csv(f'{metadata_path}{collection}.csv', index=False)

# Check for extra and missing files
missing_files_df = df[df['file_size_mb'] == 0]
missing_files_df.to_csv(f'{metadata_path}missing_files.csv', index=False)

geotiffs_in_directory = [f for f in os.listdir(geotiff_path) if os.path.isfile(os.path.join(geotiff_path, f))]
geotiffs_not_in_collection_df = [file for file in geotiffs_in_directory if file not in [f'{id}.tif' for id in df['id'].tolist()]]
extra_geotiff = {'extra_path': geotiffs_not_in_collection_df}
extra_df = pd.DataFrame(extra_geotiff)
extra_df.to_csv(f'{metadata_path}extra_geotiffs.csv', index=False)
