# Setup
```bash
git clone https://github.com/nguyen-brat/report_gen.git
cd report_gen
conda create -n "report_gen" python==3.8 -y
conda activate report_gen
pip install requirements.txt

mkdir model
mkdir model/craft
cd model/craft
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' -O "craft_mlt_25k.pth"
gdown 1XSaFwBkOaFOdtk4Ane3DFyJGPRw6v5bO
cd ..
mkdir model/ocr
cd model/ocr
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=12rZ6Y0k_plUXjfzi_FUYoudFMlVzTtXh' -O transformerocr.pth
```
Note: if can't download the ocr model download this gg drive link https://drive.google.com/file/d/12rZ6Y0k_plUXjfzi_FUYoudFMlVzTtXh/view?usp=drive_link

# Run sample