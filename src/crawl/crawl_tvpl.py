from selenium import webdriver
import time
import os
import requests
from base import BaseCrawlTool
from ..dataprocessing.unzip import unzip

class TVPLCrawler(BaseCrawlTool):
    def __init__(
            self,
            web_link = "https://thuvienphapluat.vn",
            save_directory = "/home/nguyen/Documents/data/thuvienphapluat",
            headless=False,
    ):
        super.__init__(web_link, save_directory, headless)

    def __call__(self, key="102/2004/NĐ-CP"):
        # Typing login information
        self.sendkey_by_xpath("//input[@id=\"usernameTextBox\"]", "nguyen_brat", self.driver, self.wait)
        self.sendkey_by_xpath("//input[@id=\"passwordTextBox\"]", "Kim@2972003", self.driver, self.wait)

        # Click login button
        self.click_by_xpath("//input[@id=\"loginButton\"]", self.driver, self.wait)
        time.sleep(2)

        # Send key document
        self.sendkey_by_xpath("//input[@id=\"txtKeyWord\"]", key, self.driver, self.wait)
        # Click search button
        self.click_by_class("//input[@id=\"btnKeyWordHome\"]", self.driver, self.wait)
        time.sleep(2)

        # first_doc = driver.find_element("xpath", "//*[@id=\"block-info-advan\"]/div[2]/div[1]/div[1]/div[2]/p[1]/a")
        # first_doc.click()
        self.click_by_xpath("//*[@id=\"block-info-advan\"]/div[2]/div[1]/div[1]/div[2]/p[1]/a", self.driver, self.wait)
        time.sleep(3)

        # down_page = driver.find_element("xpath", "//*[@id=\"aTabTaiVe\"]")
        # down_page.click()
        self.click_by_xpath("//*[@id=\"aTabTaiVe\"]")
        time.sleep(1)

        # click to the  download button
        success_flag = self.click_by_xpath("//*[@id=\"ctl00_Content_ctl00_vietnameseHyperLink\"]", self.driver, self.wait)
        #download.click()
        time.sleep(2)
        # close window
        self.driver.quit()
        metadata = None

        #unzip the downloaded file
        unzip(self.save_directory+"/*.zip", remove_zip=True)

        return success_flag, metadata
    
    def download_file(self, url):
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Open the file in binary mode and write the contents to it
                with open(self.save_directory, 'wb') as file:
                    file.write(response.content)
                return True  # Download was successful
            else:
                return False  # Failed due to non-200 status code
        except Exception as e:
            print(f"An error occurred: {e}")
            return False  # Failed due to an exception
    
if __name__ == "__main__":
    pass
# https://thuvienphapluat.vn/documents/download.aspx?id=Zh6zpwFO93RlbTvbZo90hg%3d%3d&amp;part=-1
# https://thuvienphapluat.vn/documents/download.aspx?id=Zh6zpwFO93RlbTvbZo90hg%3d%3d&part=-1