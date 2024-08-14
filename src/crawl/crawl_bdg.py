from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import sys
import os
from typing import List
from glob import glob

from base import BaseCrawlTool

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

class BGDCrawler(BaseCrawlTool):
    def __init__(
            self,
            web_link = "https://vpdt.vnptioffice.vn/qlvbdh_hcm/main?lang=vi",
            save_directory = "/home/nguyen/Documents/data/vanbansgd_hcm/bao_cao2",
            headless=False,
    ):
        super().__init__(web_link, save_directory, headless)
        self.doc_categories = ['CONGVAN', 'BAOCAO', 'BIENBAN', 'CONGDIEN', 'HUONGDAN', 'KEHOACH', 'NGHIDINH', 'KETLUAN','NGHIQUYET'
                                'QUYDINH', 'QUYETDINH', 'THONGBAO', 'THONGTU', 'THONGTULIENTICH', 'TOTRINH', 'CHUONGTRINH', 'HOPDONG',
                                'HOPDONGLAODONG', 'BAOCAOTUAN', 'KHAC', 'PHIEUTRINH', 'GUQ', 'GIAYMOI', 'PHIEUCHUYEN', 'VANBANNOIBO',
                                'GIAYNGHIPHEP', 'GIAYGIOITHIEU', 'DEAN']


    def __call__(self, key):
        success_flag = self.collect_by_name([key])
        return success_flag
    

    def collect_by_name(self, keys:List[str], category:str="so_ky_hieu"):
        '''
        Download a file by search name. Only download the first matched

        Args:
            category: The category of keys include:
                    - trich_yeu
                    - so_ky_hieu
                    - soden
                    - don_vi_ban_hanh
                    - ngay_van_ban
                    - ngay_den
                    - do_khan
                    - nguoi_soan_thao

        Return:
            'Bool': return true if download all success and false if not one of it not success
        '''
        #type username
        self.sendkey_by_xpath("//*[@id=\"userName\"]", "vanthu.sgd", self.driver, self.wait)
        #type password
        self.sendkey_by_xpath("//*[@id=\"passWord\"]", "Sgd123aA@", self.driver, self.wait)
        #click login button
        self.click_by_xpath("//*[@id=\"submitBtn\"]", self.driver, self.wait)
        time.sleep(2)
        #click quan li van ban
        self.click_by_xpath("//*[@id=\"full_menu\"]/li[2]/a/b", self.driver, self.wait)
        time.sleep(2)
        #click da ban hanh
        self.click_by_xpath("//*[@id=\"m2270\"]", self.driver, self.wait)
        # click select type
        self.click_by_xpath("//*[@id=\"btnVB_dsvb\"]", self.driver, self.wait)
        # click type
        if category == "trich_yeu":
            self.click_by_xpath("//*[@id=\"li_txt_trich_yeu\"]", self.driver, self.wait)
        elif category == "so_ky_hieu":
            self.click_by_xpath("//*[@id=\"li_txt_so_kyhieu\"]", self.driver, self.wait)
        elif category == "soden":
            self.click_by_xpath("//*[@id=\"li_txt_so_den\"]", self.driver, self.wait)
        elif category == "don_vi_ban_hanh":
            self.click_by_xpath("//*[@id=\"menusearchVanBan_dsvb\"]/li[5]/a", self.driver, self.wait)
        elif category == "ngay_van_ban":
            self.click_by_xpath("//*[@id=\"menusearchVanBan_dsvb\"]/li[7]/a", self.driver, self.wait)
        elif category == "ngay_den":
            self.click_by_xpath("//*[@id=\"menusearchVanBan_dsvb\"]/li[8]/a", self.driver, self.wait)
        elif category == "do_khan":
            self.click_by_xpath("//*[@id=\"menusearchVanBan_dsvb\"]/li[9]/a", self.driver, self.wait)
        elif category == "nguoi_soan_thao":
            self.click_by_xpath("//*[@id=\"menusearchVanBan_dsvb\"]/li[17]/a", self.driver, self.wait)
        else:
            raise ValueError(f"Not support category {category}")
        time.sleep(2)

        success_flags = []
        for key in keys:
            # send key
            self.sendkey_by_xpath("//*[@id=\"txtSearchDsvb\"]", key, self.driver, self.wait)
            time.sleep(2)
            # click tim kiem button
            self.click_by_xpath("//*[@id=\"btnSearchVB_dsvb\"]", self.driver, self.wait)
            time.sleep(2)
            # click first document
            self.click_by_xpath("/html/body/div[8]/div[6]/div[2]/table/tbody/tr/td[8]")
            time.sleep(2)
            # collect document metadata
            metadata = self.collect_document_information()
            # click download document
            success_flag = self.click_by_xpath("//*[@id=\"zipall\"]", self.driver, self.wait)
            success_flags.append(success_flag)
            time.sleep(2)
            # click close button
            self.click_by_xpath("//*[@id=\"close-row-ttvb\"]", self.driver, self.wait)
        # close window
        self.driver.quit()

        for success_flag in success_flags:
            if not success_flag:
                return False, None
        return True, metadata


    def collect_by_category(self, collect_type="BAOCAO"):
        '''
        Download the documents by category
        all category:
        - CONGVAN, BAOCAO, BIENBAN, CONGDIEN, HUONGDAN, KEHOACH, NGHIDINH, KETLUAN,NGHIQUYET
        QUYDINH, QUYETDINH, THONGBAO, THONGTU, THONGTULIENTICH, TOTRINH, CHUONGTRINH, HOPDONG,
        HOPDONGLAODONG, BAOCAOTUAN, KHAC, PHIEUTRINH, GUQ, GIAYMOI, PHIEUCHUYEN, VANBANNOIBO
        GIAYNGHIPHEP, GIAYGIOITHIEU, DEAN. 
        '''
        if collect_type not in self.doc_categories:
            print(f"{collect_type} not in support type which is {self.doc_categories}")
            self.driver.quit()
            return None
        #type username
        self.sendkey_by_xpath("//*[@id=\"userName\"]", "vanthu.sgd", self.driver, self.wait)
        #type password
        self.sendkey_by_xpath("//*[@id=\"passWord\"]", "Sgd123aA@", self.driver, self.wait)
        #click login button
        self.click_by_xpath("//*[@id=\"submitBtn\"]", self.driver, self.wait)
        time.sleep(2)
        #click quan li van ban
        self.click_by_xpath("//*[@id=\"full_menu\"]/li[2]/a/b", self.driver, self.wait)
        time.sleep(2)
        #click da ban hanh
        self.click_by_xpath("//*[@id=\"m2270\"]", self.driver, self.wait)
        time.sleep(2)
        # click tim kiem nang cao button
        self.click_by_xpath("/html/body/div[8]/div[4]/div/div[3]/button", self.driver, self.wait)
        time.sleep(2)
        # click another tim kiem nang cao button
        self.click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/span", self.driver, self.wait)
        time.sleep(2)
        # # click chon hinh thuc button
        self.select_from_drop_down(self.driver, self.wait, xpath="//*[@id=\"dcm_type\"]", choose_element=collect_type, max_retries=5 )
        time.sleep(2)
        # click tim kiem button
        self.click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[4]/div/button[1]", self.driver, self.wait)
        time.sleep(5)
        self.select_from_drop_down(self.driver, self.wait, xpath="//*[@id=\"selectPageRec\"]", choose_element="100", max_retries=5)
        time.sleep(2)

        # create empty metadata file
        if not os.path.exists("data/metadata.json"):
            with open("data/metadata.json", 'w', encoding='utf-8') as file:
                json.dump({}, file)
            print(f"Created empty JSON file: data/metadata.json")
        else:
            print(f"JSON file already exists: data/metadata.json")

        # download in every page
        element = self.driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
        id_attribute = element.get_attribute("id")
        print(f'id attribute is: {id_attribute}')
        # print(id_attribute-1)
        current_page = 1
        while id_attribute == '':
            print(f"=================== current page is: {current_page} ===================")
            current_page += current_page
            self.download_onepage_routing(self.driver, self.wait)
            element = self.driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            id_attribute = element.get_attribute("id")
            time.sleep(2)
            self.remove_redundant(self.save_directory)
        self.driver.quit()

    def collect_document_information(self):
        # trich yeu: //*[@id="detailTrichYeu"]
        # so ki hieu: //*[@id="detailSoKyHieu"]
        # don vi ban hanh: //*[@id="div_donvi_soanthao"]
        # ngay den: //*[@id="detail_ngay_den_banhanh_data"]
        # so van ban: //*[@id="dt_thongtin_vanban"]/tbody/tr[4]/td[4]
        # so den: //*[@id="dt_thongtin_vanban"]/tbody/tr[4]/td[6]
        # van ban: //*[@id="detail_vb_noingoai"]
        # van ban giay: //*[@id="detail_vb_giay"]
        # do mat: //*[@id="td_secret_level"]
        # loai van ban: //*[@id="dt_thongtin_vanban"]/tbody/tr[8]/td[2]
        # hinh thuc: //*[@id="dt_thongtin_vanban"]/tbody/tr[8]/td[4]
        # do khan: //*[@id="dt_thongtin_vanban"]/tbody/tr[8]/td[6]
        # nguoi soan thao: //*[@id="id_nguoi_soan"]
        # van ban lien quan: //*[@id="dt_thongtin_vanban"]/tbody/tr[13]/td[2]
        # ngay het han: //*[@id="divNhacNhoHanXuLy"]/td[2]
        # ghi chu: //*[@id="trGhiChu"]/td[2]
        # but phe chi dao: //*[@id="trYKienChiDao"]/td[2]
        # don vi du kien nhan: //*[@id="tdDonViDuKienNhan"]
        # file button: //*[@id="div_file_attach_dsvb"] //*[@id="div_file_attach_dsvb"]/div[1]/span/span

        file_attach_element = self.driver.find_element("xpath", "//*[@id=\"div_file_attach_dsvb\"]")
        file_elements = file_attach_element.find_elements("xpath", './div')
        file_names = []
        for file_element in file_elements:
            file_names.append(file_element.find_element("xpath", './span/span').text)

        result = {
            self.driver.find_element("xpath", "//*[@id=\"detailSoKyHieu\"]").text: {
                "trich_yeu": self.driver.find_element("xpath", "//*[@id=\"detailTrichYeu\"]").text,
                "don_vi_ban_hanh":self.driver.find_element("xpath", "//*[@id=\"div_donvi_soanthao\"]").text,
                "ngay_den":self.driver.find_element("xpath", "//*[@id=\"detail_ngay_den_banhanh_data\"]").text,
                "so_van_ban":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[4]/td[4]").text,
                "so_den":self.driver.find_element("xpath", "//*[@id=\"detail_vb_noingoai\"]").text,
                "van_ban":self.driver.find_element("xpath", "//*[@id=\"detail_vb_noingoai\"]").text,
                "van_ban_giay":self.driver.find_element("xpath", " //*[@id=\"detail_vb_giay\"]").text,
                "do_mat":self.driver.find_element("xpath", "//*[@id=\"td_secret_level\"]").text,
                "loai_van_ban":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[2]").text,
                "hinh_thuc":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[4]").text,
                "do_khan":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[6]").text,
                "nguoi_soan_thao":self.driver.find_element("xpath", "//*[@id=\"id_nguoi_soan\"]").text,
                "van_ban_lien_quan":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[13]/td[2]").text,
                "ngay_het_han":self.driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[13]/td[2]").text,
                "ghi_chu":self.driver.find_element("xpath", "//*[@id=\"trGhiChu\"]/td[2]").text,
                "but_phe_chi_dao":self.driver.find_element("xpath", "//*[@id=\"trYKienChiDao\"]/td[2]").text,
                "don_vi_kien_nhan":self.driver.find_element("xpath", "//*[@id=\"tdDonViDuKienNhan\"]").text,
                "file_names":file_names
            }
        }
        return result

    def download_onepage_routing(self, driver, wait):
        time.sleep(3)
        body_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"dt_basic\"]/tbody")))
        documents_body = body_element.find_elements("xpath", './tr')
        for i, document_body in enumerate(documents_body):
            # click select document
            try:
                flag = self.click_by_xpath(f"//*[@id=\"dt_basic\"]/tbody/tr[{i+1}]", driver, wait, max_retries=5)
                if flag == False:
                    print(f"fail at try to click document {i}")
                    pass
                print(f"select document {i} success")
                time.sleep(4)
                # download zip file
                flag = self.click_by_xpath("//*[@id=\"zipall\"]", driver, wait, max_retries=5)
                if flag == False:
                    print(f"fail at try to download document {i}")
                    pass
                print(f"download document {i} success")
                time.sleep(4)
                # close document
                flag = self.click_by_xpath("//*[@id=\"close-row-ttvb\"]", driver, wait, max_retries=5)
                if flag == False:
                    print(f"fail at try to close document {i}")
                    pass
                print(f"close document {i} success")
                time.sleep(4)
                result = self.collect_document_information()
                time.sleep(4)
                if result != {}:
                    with open("data/metadata.json", "r", encoding='utf-8') as f:
                        data = json.load(f)
                    data.update(result)
                    # Write the updated data back to the file
                    with open("data/metadata.json", 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Error in download_onepage_routing at iteration {i}: {e}")

        # click next page
        time.sleep(4)
        flag = False
        locator = (By.XPATH, "//*[@id=\"pn2\"]/div[1]/ul")
        pagination = wait.until(EC.presence_of_element_located(locator))
        while flag == False: # //*[@id="pn2"]/div[1]/ul
            #flag = click_by_xpath(f'/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a', driver, wait, max_retries=5)
            for num_try in range(5):
                try:
                    next_button_ = pagination.find_element(By.XPATH, "//i[contains(@class, 'fa fa-forward')]")
                    next_button = next_button_.find_element(By.XPATH, "..")
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    next_button.click()
                    flag = True
                    break
                except Exception as e:
                    print(f"Atemp {num_try + 1} to click to next page fail got error: {e}")
                    flag = False
                    time.sleep(4)
            print("fail to click next page")
        print("success click next page")
        time.sleep(6)
        return None

if __name__ == "__main__":
    crawler = BGDCrawler()
    crawler.collect_by_category()