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

class BaseCrawlTool:
    def __init__(
            self,
            web_link = "https://vpdt.vnptioffice.vn/qlvbdh_hcm/main?lang=vi",
            save_directory = "/home/nguyen/Documents/data/vanbansgd_hcm/bao_cao2",
            headless=False,
    ):
        self.save_directory = save_directory
        self.web_link = web_link
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": save_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        if headless:
            # options.add_experimental_option("prefs", {
            #     "profile.default_content_setting_values.notifications": 2
            # })
            options.add_experimental_option("detach", True)
            options.add_argument("--headless")
            options.add_argument(f"--window-size=2560,1080")
            options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(web_link)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def remove_redundant(self, abstract_path):
        paths = glob(abstract_path + "/*.zip")
        for path in paths:
            try:
                if '(' in path:
                    os.remove(path)
            except Exception as e:
                print(f"remove folder {path} got error {e}")

    def click_by_xpath(self, xpath, driver, wait, max_retries=3):
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

    def select_from_drop_down(self, driver, wait, xpath, choose_element=100, max_retries=3):
        for attempt in range(max_retries):
            try:
                dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
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

    def click_by_class(self, class_name, driver, wait, max_retries=3):
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

    def sendkey_by_xpath(self, xpath, key, driver, wait, max_retries=3):
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