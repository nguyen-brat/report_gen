from glob import glob
import os
import sys
import tqdm
import re
from dataclasses import dataclass

from .extract_text import PdfOCR
from pdf2image import convert_from_path
import pdfplumber
import docx
import cv2
from PIL import Image
import numpy as np
import pandas as pd

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
            print(results)
            print("----------------------------")
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
        # Read the XLS file
        df = pd.read_excel(docx_path)
        return df.to_string(index=False)

    def isScan_pdf(self, doc:str):
        '''
        The scan pdf will give error font parse or empty string
        '''
        if doc == '':
            return True
        for charac in doc:
            if charac in self.char_space:
                continue
            else:
                return True
        return False
    
    def rotate_image(self, image_path):
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


class DocGraph:
    '''
    Find the name of document and other document mentioned
    '''
    def __init__(self, config):
        self.document_regex = r'^\d{1,5}/(?:-?BC)(?:-[A-Z0-9.]+)?$'
        pass

    def __call__(self, data_paths="data/bao_cao_unzip"):
        pass

    @staticmethod
    def mentioned_doc_extract(document:str):
        '''
        extract mentioned document in the document
        using regex
        '''
        document = re.sub(r' +', ' ', document)
        mentioned_document = re.findall(r'^\d{1,5}/(?:-?BC)(?:-[A-Z0-9.]+)?$', document)

    def get_instruction_template(self):
        pass

if __name__ == "__main__":
    pass