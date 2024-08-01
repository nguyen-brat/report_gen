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
from glob import glob

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

def remove_redundant(abstract_path):
    paths = glob(abstract_path + "/*.zip")
    for path in paths:
        try:
            if '(' in path:
                os.remove(path)
        except Exception as e:
            print(f"remove folder {path} got error {e}")

def click_by_xpath(xpath, driver, wait, max_retries=3):
    for attempt in range(max_retries):
        try:
            locator = (By.XPATH, xpath)
            button = wait.until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to click element with xpath {xpath}: {e}")
            time.sleep(4)  # Wait a bit before retrying
    return False

def select_from_drop_down(driver, wait, choose_element=100, max_retries=3):
    for attempt in range(max_retries):
        try:
            dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"selectPageRec\"]")))
            driver.execute_script("arguments[0].scrollIntoView();", dropdown_element)
            select = Select(dropdown_element)
            # Select the option with value "100"
            select.select_by_value(f"{choose_element}")
            time.sleep(7)
            print("successfull choose drop-down list")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to choose drop down: {e}")
            time.sleep(4)
    return False

def click_by_class(class_name, driver, wait, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Use CSS selector instead of CLASS_NAME
            locator = (By.CSS_SELECTOR, f".{class_name}")
            button = wait.until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            
            # Try regular click first
            try:
                button.click()
            except ElementClickInterceptedException:
                # If regular click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", button)
            
            return True
        except TimeoutException:
            print(f"Attempt {attempt + 1} failed: Element with class '{class_name}' not found or not clickable")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
        
        time.sleep(4)  # Wait before retrying
    
    return False

def sendkey_by_xpath(xpath, key, driver, wait, max_retries=3):
    for attempt in range(max_retries):
        try:
            locator = (By.XPATH, xpath)
            button = wait.until(EC.presence_of_element_located(locator))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.send_keys(key)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to send keys to element with xpath {xpath}: {e}")
            time.sleep(1)  # Wait a bit before retrying
    return False

def collect_document_information(driver):
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

    file_attach_element = driver.find_element("xpath", "//*[@id=\"div_file_attach_dsvb\"]")
    file_elements = file_attach_element.find_elements("xpath", './div')
    file_names = []
    for file_element in file_elements:
        file_names.append(file_element.find_element("xpath", './span/span').text)

    result = {
        driver.find_element("xpath", "//*[@id=\"detailSoKyHieu\"]").text: {
            "trich_yeu": driver.find_element("xpath", "//*[@id=\"detailTrichYeu\"]").text,
            "don_vi_ban_hanh":driver.find_element("xpath", "//*[@id=\"div_donvi_soanthao\"]").text,
            "ngay_den":driver.find_element("xpath", "//*[@id=\"detail_ngay_den_banhanh_data\"]").text,
            "so_van_ban":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[4]/td[4]").text,
            "so_den":driver.find_element("xpath", "//*[@id=\"detail_vb_noingoai\"]").text,
            "van_ban":driver.find_element("xpath", "//*[@id=\"detail_vb_noingoai\"]").text,
            "van_ban_giay":driver.find_element("xpath", " //*[@id=\"detail_vb_giay\"]").text,
            "do_mat":driver.find_element("xpath", "//*[@id=\"td_secret_level\"]").text,
            "loai_van_ban":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[2]").text,
            "hinh_thuc":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[4]").text,
            "do_khan":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[8]/td[6]").text,
            "nguoi_soan_thao":driver.find_element("xpath", "//*[@id=\"id_nguoi_soan\"]").text,
            "van_ban_lien_quan":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[13]/td[2]").text,
            "ngay_het_han":driver.find_element("xpath", "//*[@id=\"dt_thongtin_vanban\"]/tbody/tr[13]/td[2]").text,
            "ghi_chu":driver.find_element("xpath", "//*[@id=\"trGhiChu\"]/td[2]").text,
            "but_phe_chi_dao":driver.find_element("xpath", "//*[@id=\"trYKienChiDao\"]/td[2]").text,
            "don_vi_kien_nhan":driver.find_element("xpath", "//*[@id=\"tdDonViDuKienNhan\"]").text,
            "file_names":file_names
        }
    }
    return result

def download_onepage_routing(driver, wait):
    time.sleep(3)
    body_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"dt_basic\"]/tbody")))
    documents_body = body_element.find_elements("xpath", './tr')
    for i, document_body in enumerate(documents_body):
        # click select document
        try:
            flag = click_by_xpath(f"//*[@id=\"dt_basic\"]/tbody/tr[{i+1}]", driver, wait, max_retries=5)
            if flag == False:
                print(f"fail at try to click document {i}")
                pass
            print(f"select document {i} success")
            time.sleep(4)
            # download zip file
            flag = click_by_xpath("//*[@id=\"zipall\"]", driver, wait, max_retries=5)
            if flag == False:
                print(f"fail at try to download document {i}")
                pass
            print(f"download document {i} success")
            time.sleep(4)
            # close document
            flag = click_by_xpath("//*[@id=\"close-row-ttvb\"]", driver, wait, max_retries=5)
            if flag == False:
                print(f"fail at try to close document {i}")
                pass
            print(f"close document {i} success")
            time.sleep(4)
            result = collect_document_information(driver)
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
    web = "https://vpdt.vnptioffice.vn/qlvbdh_hcm/main?lang=vi"
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/home/nguyen/Documents/data/vanbansgd_hcm/bao_cao2"}
    options.add_experimental_option("prefs", prefs)
    # options.add_experimental_option("prefs", {
    #     "profile.default_content_setting_values.notifications": 2
    # })
    # options.add_experimental_option("detach", True)
    # options.add_argument("--headless")
    # options.add_argument(f"--window-size=2560,1080")
    # options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(web)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    #type username
    sendkey_by_xpath("//*[@id=\"userName\"]", "vanthu.sgd", driver, wait)
    #type password
    sendkey_by_xpath("//*[@id=\"passWord\"]", "Sgd123aA@", driver, wait)
    #click login button
    click_by_xpath("//*[@id=\"submitBtn\"]", driver, wait)
    time.sleep(2)
    #click quan li van ban
    click_by_xpath("//*[@id=\"full_menu\"]/li[2]/a/b", driver, wait)
    time.sleep(2)
    #click da ban hanh
    click_by_xpath("//*[@id=\"m2270\"]", driver, wait)
    time.sleep(2)
    # click tim kiem nang cao button
    click_by_xpath("/html/body/div[8]/div[4]/div/div[3]/button", driver, wait)
    time.sleep(2)
    # click another tim kiem nang cao button
    click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/span", driver, wait)
    time.sleep(2)
    # click chon hinh thuc button
    click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[3]/div[3]/div/div[2]/span/div/button", driver, wait)
    time.sleep(2)
    # click bao cao button
    click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[3]/div[3]/div/div[2]/span/div/ul/li[4]/a/label/input", driver, wait)
    time.sleep(2)
    # click tim kiem button
    click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[4]/div/button[1]", driver, wait)
    time.sleep(5)
    select_from_drop_down(driver, wait, choose_element="100", max_retries=5)
    time.sleep(2)

    # create empty metadata file
    if not os.path.exists("data/metadata.json"):
        with open("data/metadata.json", 'w', encoding='utf-8') as file:
            json.dump({}, file)
        print(f"Created empty JSON file: data/metadata.json")
    else:
        print(f"JSON file already exists: data/metadata.json")

    # download in every page
    element = driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
    id_attribute = element.get_attribute("id")
    print(f'id attribute is: {id_attribute}')
    # print(id_attribute-1)
    current_page = 1
    while id_attribute == '':
        print(f"=================== current page is: {current_page} ===================")
        current_page += current_page
        download_onepage_routing(driver, wait)
        element = driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        id_attribute = element.get_attribute("id")
        time.sleep(2)
        remove_redundant("/home/nguyen/Documents/data/vanbansgd_hcm/bao_cao2")
    driver.quit()