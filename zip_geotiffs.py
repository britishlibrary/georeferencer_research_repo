import zipfile
import pandas as pd
import zipfile
import os
import shutil
import pdb

ext_drive_path = '/Volumes/VERBATIM HD'
# collection = 'osdrawings'
collection = 'goad'
# Also change name of containing folder for files based on collection

ssheet_path = f'./xlsxs/{collection}.xlsx'
metadata_path = f'./metadata/{collection}/'
metadata_groups_path = f'./metadata/{collection}/metadata_groups/'
geotiff_path = f'{ext_drive_path}/georef_geotiffs/{collection}/'
zip_path = f'{ext_drive_path}/repo_zip_groups/{collection}/'

if not os.path.isdir(zip_path):
    os.makedirs(zip_path)
if not os.path.isdir(metadata_groups_path):
    os.makedirs(metadata_groups_path)

def zip_files(zip_filename, file_list, folder):
    # Create a new ZIP file
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in file_list:
            print(f'./{folder}/{os.path.basename(file)}')
            zipf.write(file, f'./{folder}/{os.path.basename(file)}')
    zipf.close()

groups_files = [os.path.join(metadata_groups_path, f) for f in os.listdir(metadata_groups_path)]
groups_files = [item for item in groups_files if not '.DS_Store' in item]

# All OSDrawings with two maps on same sheet
subsidiary_two_files = []
for folder, subfolders, files in os.walk(geotiff_path):
    for file in files:
        file_path = os.path.join(folder, file)
        if '_2' in file_path:
            subsidiary_two_files.append(file_path)

# if __name__ == "__main__":
for f in groups_files:
    df = pd.read_csv(f)
    ids = df['id'].tolist()

    to_zip_files = [geotiff_path + id + '.tif' for id in ids if os.path.exists(geotiff_path + id + '.tif')]

    for zf in to_zip_files:
         file_second_map = geotiff_path + os.path.splitext(os.path.basename(zf))[0] + '_2' + '.tif'
         if file_second_map in subsidiary_two_files:
             to_zip_files.append(file_second_map)

    letter_zip_fname = os.path.splitext(os.path.basename(f))[0]

    # CHANGE name of containing folder for zip files based on collection
    # osdrawings
    # letter = letter_zip_fname[0]
    # goad - not letter but city name
    letter = letter_zip_fname.split(' zip')[0]

    zip_letter_path = f'{zip_path}/{letter}/'
    if not os.path.isdir(zip_letter_path):
        os.makedirs(zip_letter_path)

    zip_filename = f'{zip_letter_path}{letter_zip_fname}.zip'

    ssheet_filename = f'{metadata_groups_path}{letter_zip_fname}.csv'
    shutil.copy(ssheet_filename, f'{zip_letter_path}{letter_zip_fname}.csv')

    # Call the function to zip the files
    zip_files(zip_filename, to_zip_files, letter)
