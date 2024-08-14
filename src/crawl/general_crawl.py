

from typing import List
from glob import glob
from typing import List
from base import BaseCrawlTool
from crawl_bdg import BGDCrawler
from crawl_tvpl import TVPLCrawler

class CrawlOnlineTool:
    def __init__(
            self,
            save_directory:str,
            tools_box:List[BaseCrawlTool]=[BGDCrawler, TVPLCrawler],
    ):
        
        self.tool_boxs = [tool(save_directory=save_directory) for tool in tools_box]

    def getdoc(self, keys:List[str]):
        '''
        Get document from document number only. for ex: ["102/2004/NĐ-CP"]

        Args:
            keys: List of document need to crawl
        Return:
            'Dict/None': return metadata of that document if crawl successfully
        '''
        metadatas = []
        for key in keys:
            sucess_flag = False
            for tool in self.tool_boxs:
                sucess_flag, metadata  = tool(key)
                if sucess_flag:
                    metadatas.append(metadata)
                    break
                else:
                    pass
            if sucess_flag:
                print(f"download document {key} successfully !")
            else:
                print(f"download document {key} not success !")
        return metadatas