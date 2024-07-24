import zipfile
from glob import glob
from tqdm import tqdm

# Replace 'your_zip_file.zip' with the actual path to your zip file
# Replace 'destination_folder' with the path to the target directory
folder_paths = glob('data/vanbang_raw/*')
for folder_path in tqdm(folder_paths):
    folder_name = folder_path.split('/')[-1].split('.')[0]
    with zipfile.ZipFile(folder_path, 'r') as zip_ref:
        zip_ref.extractall(f'data/vanbanunzip/{folder_name}')