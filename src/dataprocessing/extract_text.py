import matplotlib.pyplot as plt
from PIL import Image
import subprocess

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from os.path import join as osp
import sys
from glob import glob
import shutil
import numpy as np
import cv2
from tqdm import tqdm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import DBSCAN
from glob import glob
import os
from dataclasses import dataclass

from .extract_text import PdfOCR
from pdf2image import convert_from_path
import pdfplumber
import docx
from PIL import Image
import pandas as pd

from ocr import PdfOCR

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

@dataclass
class DocumentReaderConfig:
    model_path: str = 'model/ocr/transformerocr.pth'
    model_type: str = 'vgg_transformer'
    device: str = 'cuda:0'
    script_path: str = 'script/script.sh'
    n_neighbors: int =1 # n-neighbor for outlier classify using k-nearest neighbor
    eps: int =2.8 # eps in dbscan (eps = mean_bbox_text_length * eps)
    min_samples: int =2 # min sample parameter used in dbscan

class PdfParser:
    def predict(self, pdf_path):
        result = ""
        pdf = self.pdf_parsing(pdf_path)
        for page in pdf.pages:
            result += page.extract_text()
        return result

    def pdf_parsing(self, pdf_path):
        return pdfplumber.open(pdf_path)

class DocumentReader:
    '''
    Parser all document include scan pdf, pdf, docx to text
    '''
    def __init__(
            self,
            config:DocumentReaderConfig=DocumentReaderConfig()
    ):
        self.config = config
        self.char_space = "aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvwxyýỳỷỹỵAÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬBCDĐEÉÈẺẼẸÊẾỀỂỄỆFGHIÍÌỈĨỊJKLMNOÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢPQRSTUÚÙỦŨỤƯỨỪỬỮỰVWXYÝỲỶỸỴ0123456789.,!?()[]{}:;-_+=<>/@#$%^&*\n\t\r\f\v "
        self.ocr_engine = PdfOCR(config.model_path, config.model_type, config.device, config.script_path)
        self.pdf_parser_enginer = PdfParser()

    def predict(self, document_path):
        file_extention = document_path.split('.')[-1]
        if file_extention == 'pdf':
            result = self.transform_pdf(document_path)
            if self.isScan_pdf(result):
                result = self.transform_ocr(document_path)
        elif file_extention == 'docx' or file_extention == 'doc':
            result = self.transform_docx(document_path)
        elif file_extention in ['jpeg', 'png', 'jpg']:
            result = self.transform_image(document_path)
        elif file_extention == 'xls':
            result = self.transform_xls(document_path)
        else:
            raise TypeError(f"Not support the {file_extention} extention document")

        return result
    
    def transform_image(self, image_path, enable_straingt_transform=False):
        if enable_straingt_transform:
            image = self.rotate_image(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        else:
            image = Image.open(image_path)
        result = self.ocr_engine.predict(
            image,
            self.config.n_neighbors,
            self.config.eps,
            self.config.min_samples
        )
        return result

    def transform_ocr(self, pdf_path):
        results = ''
        images = convert_from_path(pdf_path)
        for image in images:
            results += self.ocr_engine.predict(
                image,
                self.config.n_neighbors,
                self.config.eps,
                self.config.min_samples
            ) + '\n'
        return results.strip()

    def transform_pdf(self, pdf_path):
        return self.pdf_parser_enginer.predict(pdf_path)

    def transform_docx(self, docx_path):
        doc = docx.Document(docx_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)
    
    def transform_xls(self, docx_path):
        '''
        This function read file with xls extention
        and return the text of it using library.
        '''
        # Read the XLS file
        df = pd.read_excel(docx_path)
        return df.to_string(index=False)

    def isScan_pdf(self, doc:str):
        '''
        This function will check the doc is scan or not.
        The scan pdf will give error font parse or empty string

        Args:
            doc: extracted text by using pdf parser libary (not ocr)
        Return:
            'bool': return true if document is scan and false if not scan
        '''
        if doc == '':
            return True
        for charac in doc:
            if charac in self.char_space:
                continue
            else:
                return True
        return False
    
    @staticmethod
    def rotate_image(image_path:str):
        '''
        This function rotate the image if it not straght
        Args:
            image_path: the path to needed rotated image
        Return:
            cv2.Image: return cv2 image
        '''
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        # Use Hough Line Transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        if lines is not None:
            # Find the dominant line angle
            angles = [line[0][1] for line in lines]
            dominant_angle = np.median(angles)
            # Convert angle to degrees
            angle_degrees = np.degrees(dominant_angle)
            # Adjust angle to straighten the image
            if angle_degrees < 45:
                rotation_angle = angle_degrees
            elif angle_degrees < 135:
                rotation_angle = angle_degrees - 90
            else:
                rotation_angle = angle_degrees - 180
            # Rotate the image
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        else:
            return img
        
    @staticmethod
    def detect_large_circles(image_path, min_radius):
        '''
        This function to get whether the image in given path has circle bigger
        than given min_radius used to recognize carpentry mark in the picture.
        '''
        # Read the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=100,
            param2=30,
            minRadius=30,
            maxRadius=0
        )
        
        large_circles_exist = False
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                radius = circle[2]
                if radius > min_radius:
                    large_circles_exist = True
                    break
        
        return large_circles_exist

if __name__ == "__main__":
    # USE CASE OF GENERAL DOCUMENT READER
    config = DocumentReaderConfig(
        model_path = 'model/ocr/transformerocr.pth',
        model_type = 'vgg_transformer',
        device = 'cuda:0',
        script_path = 'script/script.sh',
        n_neighbors =1, # n-neighbor for outlier classify using k-nearest neighbor
        eps =2.8, # eps in dbscan (eps = mean_bbox_text_length * eps)
        min_samples =2, # min sample parameter used in dbscan)
    )
    read_engine = DocumentReader(config)
    output = read_engine("data/bao_cao_unzip/2453137/184_184. Báo cáo thực hiện chỉ thị 05 năm học 2023-2024.pdf")
    print(output)