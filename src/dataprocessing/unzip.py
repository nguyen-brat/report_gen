import zipfile
from glob import glob
from tqdm import tqdm

# Replace 'your_zip_file.zip' with the actual path to your zip file
# Replace 'destination_folder' with the path to the target directory
folder_paths = glob('data/bao_cao/*')
for folder_path in tqdm(folder_paths):
    folder_name = folder_path.split('/')[-1].split('.')[0]
    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
        zip_ref.extractall(f'data/bao_cao_unzip/{folder_name}')