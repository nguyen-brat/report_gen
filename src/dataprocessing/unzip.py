import zipfile
from glob import glob
from tqdm import tqdm
import os

# Replace 'your_zip_file.zip' with the actual path to your zip file
# Replace 'destination_folder' with the path to the target directory
def unzip(abstract_path='data/bao_cao/*', remove_zip=False):
    folder_paths = glob(abstract_path)
    for folder_path in tqdm(folder_paths):
        folder_name = folder_path.split('/')[-1].split('.')[0]
        with zipfile.ZipFile(folder_path, 'r') as zip_ref:
            zip_ref.extractall(f'data/bao_cao_unzip/{folder_name}')
    if remove_zip:
        for folder_path in tqdm(folder_paths):
            if os.path.exists(folder_path):
                os.remove(folder_path)
                
if __name__ == "__main__":
    unzip()