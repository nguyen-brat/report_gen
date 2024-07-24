from selenium import webdriver
import time
import os

web = "https://thuvienphapluat.vn"
driver = webdriver.Chrome()
driver.get(web)
driver.maximize_window()

time.sleep(6)

username = driver.find_element("xpath", "//input[@id=\"usernameTextBox\"]")
username.send_keys("nguyen_brat")

password = driver.find_element("xpath", "//input[@id=\"passwordTextBox\"]")
password.send_keys("Kim@2972003")

login_button = driver.find_element("xpath", "//input[@id=\"loginButton\"]")
login_button.click()

time.sleep(2)

finddoc = driver.find_element("xpath", "//input[@id=\"txtKeyWord\"]")
finddoc.send_keys("30/2020/NĐ-CP")
search_button = driver.find_element("xpath", "//input[@id=\"btnKeyWordHome\"]")
search_button.click()

time.sleep(2)
first_doc = driver.find_element("xpath", "//*[@id=\"block-info-advan\"]/div[2]/div[1]/div[1]/div[2]/p[1]/a")
first_doc.click()
time.sleep(3)

down_page = driver.find_element("xpath", "//*[@id=\"aTabTaiVe\"]")
down_page.click()
time.sleep(1)

download = driver.find_element("xpath", "//*[@id=\"ctl00_Content_ctl00_vietnameseHyperLink\"]")
link = download.get_attribute("href")
print(link)
#download.click()
time.sleep(2)