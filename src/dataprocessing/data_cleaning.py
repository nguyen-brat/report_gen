from glob import glob
import os
import sys
import tqdm

from extract_text import PdfOCR
from pdf2image import convert_from_path
import pdfplumber
import docx

class DocumentReaderConfig:
    model_path: str = 'src/crawl/weights/transformerocr'
    model_type: str = 'vgg_transformer'
    device: str = 'cuda:0'
    script_path: str = 'script/script.sh'
    n_neighbors=1 # n-neighbor for outlier classify using k-nearest neighbor
    eps=2.8 # eps in dbscan (eps = mean_bbox_text_length * eps)
    min_samples=2 # min sample parameter used in dbscan

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
            config:DocumentReaderConfig
    ):
        self.config = config
        self.char_space = "aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvwxyýỳỷỹỵAÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬBCDĐEÉÈẺẼẸÊẾỀỂỄỆFGHIÍÌỈĨỊJKLMNOÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢPQRSTUÚÙỦŨỤƯỨỪỬỮỰVWXYÝỲỶỸỴ0123456789.,!?()[]{}:;-_+=<>/@#$%^&*\n\t\r\f\v "
        self.ocr_engine = PdfOCR(config.model_path, config.model_type, config.device, config.script_path)
        self.pdf_parser_enginer = PdfParser()

    def __call__(self, doc_path):
        return

    def transform(self, document_path):
        file_extention = document_path.split('.')[-1]
        if file_extention == 'pdf':
            result = self.transform_pdf(document_path)
            if self.isScan_pdf(result):
                result = self.transform_ocr(document_path)
        elif file_extention == 'docx':
            result = self.transform_docx(document_path)
        else:
            raise TypeError(f"Not support the {file_extention} extention document")

        return result

    def transform_ocr(self, pdf_path):
        image = convert_from_path(pdf_path)
        return self.ocr_engine.predict(
            image,
            self.config.n_neighbors,
            self.config.eps,
            self.config.min_samples
        )

    def transform_pdf(self, pdf_path):
        return self.pdf_parser_enginer.predict(pdf_path)

    def transform_docx(self, docx_path):
        doc = docx.Document(docx_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    def isScan_pdf(self, doc:str):
        '''
        The scan pdf will give error font parse or empty string
        '''
        for charac in doc:
            if charac in self.char_space:
                continue
            else:
                return True
        return False


class DocGraph:
    '''
    Find the name of document and other document mentioned
    '''
    def __init__(self):
        pass

    def __call__(self, data_paths):
        pass

    def mentioned_extract(self, document):
        '''
        extract mentioned document in the document
        using regex
        '''
        pass

    def get_instruction_template(self):
        pass

if __name__ == "__main__":
    pass