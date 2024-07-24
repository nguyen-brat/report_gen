from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def click_by_xpath(xpath, driver, wait, max_retries=3):
    for attempt in range(max_retries):
        try:
            locator = (By.XPATH, xpath)
            button = wait.until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to click element with xpath {xpath}: {e}")
            time.sleep(2)  # Wait a bit before retrying

def sendkey_by_xpath(xpath, key, driver, wait, max_retries=3):
    for attempt in range(max_retries):
        try:
            locator = (By.XPATH, xpath)
            button = wait.until(EC.presence_of_element_located(locator))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.send_keys(key)
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to send keys to element with xpath {xpath}: {e}")
            time.sleep(1)  # Wait a bit before retrying

def download_onepage_routing(driver, wait):
    for i in range(10):
        try:
            # select document
            click_by_xpath(f'/html/body/div[8]/div[6]/div[2]/table/tbody/tr[{i+1}]/td[7]', driver, wait)
            time.sleep(2)
            print(1)
            # download zip file
            click_by_xpath(f'/html/body/div[8]/div[6]/div[2]/table/tbody/tr[{i+2}]/td/div/article/div[2]/table/tbody/tr[12]/td[2]/a', driver, wait)
            time.sleep(2)
            print(2)
            # close document
            click_by_xpath(f'/html/body/div[8]/div[6]/div[2]/table/tbody/tr[{i+2}]/td/div/article/div[1]/button[23]', driver, wait)
            print(3)
            time.sleep(3)
        except Exception as e:
            print(f"Error in download_onepage_routing at iteration {i}: {e}")
    # click next page
    click_by_xpath(f'/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a', driver, wait)
    time.sleep(5)
    return None

web = "https://vpdt.vnptioffice.vn/qlvbdh_hcm/main?lang=vi"
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": "/home/nguyen/Documents/data/vanbangg"}
options.add_experimental_option("prefs", prefs)
#options.add_argument("--headless")
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
#click quan li van ban
click_by_xpath("//*[@id=\"full_menu\"]/li[2]/a/b", driver, wait)
#click da ban hanh
click_by_xpath("//*[@id=\"m2270\"]", driver, wait)
# click tim kiem nang cao button
click_by_xpath("/html/body/div[8]/div[4]/div/div[3]/button", driver, wait)
# click another tim kiem nang cao button
click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/span", driver, wait)
# click chon hinh thuc button
click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[3]/div[3]/div/div[2]/span/div/button", driver, wait)
time.sleep(2)
# click bao cao button
click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[3]/div[3]/div/div[2]/span/div/ul/li[4]/a/label/input", driver, wait)
time.sleep(2)
# click tim kiem button
click_by_xpath("/html/body/div[8]/div[20]/div/div/div[2]/div[4]/div/button[1]", driver, wait)
time.sleep(5)
#click hinh thuc button
# click_by_xpath("/html/body/div[8]/div[6]/div[2]/table/thead/tr/th[11]", driver, wait)
# time.sleep(3)
# click_by_xpath("/html/body/div[8]/div[6]/div[2]/table/thead/tr/th[11]", driver, wait)
# time.sleep(3)

# download in every page
element = driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
id_attribute = element.get_attribute("id")
print(f'id attribute is: {id_attribute}')
# print(id_attribute-1)
current_page = 1
while id_attribute=='':
    print(f"=================== current page is: {current_page} ===================")
    current_page += current_page
    download_onepage_routing(driver, wait)
    element = driver.find_element("xpath", '/html/body/div[8]/div[8]/div[1]/ul/li[last() - 1]/a')
    id_attribute = element.get_attribute("id")
    time.sleep(2)
driver.quit()

# download
# /html/body/div[8]/div[6]/div[2]/table/tbody/tr[10]/td[7]