from glob import glob
import os
from os.path import join as osp
import sys
from tqdm import tqdm
import re
import json
from typing import List, Dict

from .extract_text import DocumentReader
from ..crawl.general_crawl import CrawlOnlineTool

from transformers import PreTrainedTokenizerBase

def extract_text(
        unzip_data_path:str,
        text_datapath:str,
        read_engine:DocumentReader,
):
    '''
    convert raw unzip data into text file. The unzip data could have alot of extention include:
        - scan/non-scan pdf
        - image (jpeg, png,...)
        - xls
        - doc
        - docx

    Args:
        unzip_data_path: the unzip extracted data path
        text_datapath: the output text data path extracted from unzip file
        read_engine: reader engine
    '''
    extention = ['pdf', 'doc', 'docx', 'jpeg', 'png', 'jpg', 'xls']
    os.makedirs(text_datapath, exist_ok=True)
    paths = glob.glob(unzip_data_path + "/*/*")
    for path in tqdm(paths):
        text_result = read_engine(path)
        file_name = ''
        if extention in path:
            file_name = path.split('/')[-1].split(extention)[0]
        if file_name == '':
            file_name = path.split('/')[-1]
        with open(osp(f'{text_datapath}', f'{file_name}.txt'), 'w') as f:
            f.write(text_result)

class DocGraph:
    '''
    Find the name of document and other document mentioned
    '''
    def __init__(
            self,
            document_reader_config:DocumentReader,
            cache_dir = "./cache"
    ):
        self.report_document_regex = r'^\d{1,5}/(?:-?BC)(?:-[A-Z0-9.]+)?$'
        self.general_document_regex = r'\b\d+/(?:\d+/)?[aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvwxyýỳỷỹỵAÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬBCDĐEÉÈẺẼẸÊẾỀỂỄỆFGHIÍÌỈĨỊJKLMNOÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢPQRSTUÚÙỦŨỤƯỨỪỬỮỰVWXYÝỲỶỸỴ0-9]+(?:-[AÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬBCDĐEÉÈẺẼẸÊẾỀỂỄỆFGHIÍÌỈĨỊJKLMNOÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢPQRSTUÚÙỦŨỤƯỨỪỬỮỰVWXYÝỲỶỸỴ0-9]+)?'
        self.read_engine = DocumentReader(document_reader_config)
        os.makedirs(cache_dir, exist_ok=True)
        self.craw_online = CrawlOnlineTool(cache_dir)

    def __call__(
            self,
            data_paths="data/bao_cao_unzip",
            general_metadata_path = "metadata/metadata.json",
            metadata_path = "metadata/metadata_report.json",
            text_datapath = "data/baocao_text",
            saved_instruction_path = "data/instruction",
    ):
        '''
        
        '''
        extention = ['pdf', 'doc', 'docx', 'jpeg', 'png', 'jpg', 'xls']
        with open(general_metadata_path, "r") as f:
            general_metadata = json.load(f)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        for key, item in metadata.items():
            file_names = item["file_names"]
            main_doc_name = file_names[0]
            if extention in main_doc_name:
                main_doc_name = main_doc_name.split(extention)[0]
            if os.path.isfile(osp(f'{text_datapath}', f'{main_doc_name}.txt')):
                with open(osp(f'{text_datapath}', f'{main_doc_name}.txt'), 'r') as f:
                    main_doc = f.read()
                mention_documents = self.mentioned_doc_extract(main_doc)
                try:
                    pass
                except:
                    pass
            else:
                metadata = self.craw_online(key)
                if metadata:
                    pass

    def mentioned_doc_extract(self, document:str):
        '''
        extract mentioned document in the document
        using regex
        '''
        document = re.sub(r' +', ' ', document)
        mentioned_documents = re.findall(self.general_document_regex, document)
        return mentioned_documents

    def get_instruction_template(
            self,
            title:str,
            synthetic_doc:str,
            related_docs:List[str],
            tokenizer:PreTrainedTokenizerBase
    )->str:
        '''
        Get prompt for LLM training

        Args:
            title: the title of document wanted to synthetic ex: THỐNG KÊ GIÁO DỤC KỲ CUỐI NĂM HỌC 2023-2024
            synthetic_doc: the output document wanted to synthetic from related document
            related_doc: all related document mention in the synthetic doc
            tokenizer: tokenizer of LLM model want to used.

        Returns:
            The prompt for LLm training
        '''
        related_docs_text = ''
        for i, doc in enumerate(related_docs):
            related_docs_text += f'Document {i+1}:\n\n{doc}'
        user_template = f'''You are a helpful assistant. Imagine you are a reporter writer for a school. \
Your task is to synthetic all given document to write a general report with a given subtitle. 
### The given documents is:
{related_docs_text}

### Synthetic document with title: {title}
'''
        message = [
            {'role': 'user', 'content':user_template},
            {'role': 'assistant', 'content':synthetic_doc}
        ]
        output_text = tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True
        )

        return output_text
    
    def get_document_by_name(self, document_name, text_path)->str:
        if os.path.isfile(osp(f"{text_path}", f"{document_name}.txt")):
            with open(osp(f"{text_path}", f"{document_name}.txt"), "r") as f:
                data = f.read()
            return data
        else:
            pass

    def get_document_by_symbol_number(self, document_number, general_metadata:Dict)->str:
        pass


if __name__ == "__main__":
    pass