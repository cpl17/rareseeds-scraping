from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import itertools
import json


PATH = "C:\Program Files (x86)\chromedriver.exe"
URL = "https://www.rareseeds.com/store"
DELAY = 20


# Open Page 

driver = webdriver.Chrome(executable_path=PATH)
driver.get(URL)


# # Traverse Categories

# WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, "//*[@id='layer-product-list']/div/div[1]")))

# for cat in [1,2,3,4,8]:
#     if cat != 0:
#         WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, f"//*[@id='layer-product-list']/div/div[{cat}]")))

#     category_element = driver.find_element_by_xpath(f"//*[@id='layer-product-list']/div/div[{cat}]")
#     print(category_element.text)
#     category_element.click()

# Heirlooms
WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, "//*[@id='layer-product-list']/div/div[1]")))
category_element = driver.find_element_by_xpath("//*[@id='layer-product-list']/div/div[1]")
print(category_element.text)
category_element.click()

#TRAVERSE SUBCATEGORY

WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, "//*[@id='layer-product-list']/div/div[1]")))

number_of_subcategories = len(driver.find_elements_by_class_name("grid--item"))
plant_dict = {}

for i in range(1,number_of_subcategories):

    #Wait for page to load every loop except the first (page is already loaded)
    if i>1:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, f"//*[@id='layer-product-list']/div/div[{i+1}]")))

    #Find and click on the subcategory element
    subcategory_element = driver.find_element_by_xpath(f"//*[@id='layer-product-list']/div/div[{i+1}]")
    subcategory_element.click()


    # Traverse Plants in Subcategory
    
    number_of_plants = len(driver.find_elements_by_class_name("product--name"))

    if i == 34:
        driver.back()
        continue

    for i in range(number_of_plants):

        if i> 0:
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, f"//*[@id='layer-product-list']/div[2]/div/div[{i+1}]/div[1]/a")))
        plant_element = driver.find_element_by_xpath(f"//*[@id='layer-product-list']/div[2]/div/div[{i+1}]/div[1]/a")
        plant_element.click()


        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.base")))

        #Get the name of the plant
        name_element = driver.find_element_by_css_selector("span.base")
        name = name_element.text


        #Get the bullet information

        def foo(xpath,name):

            '''Find ul element, extract html, use bs to extract info and store in a dictionary'''

            info_element = driver.find_element_by_xpath(xpath)
            info_html = info_element.get_attribute("innerHTML")
            soup = BeautifulSoup(info_html,'html.parser')
            info_list = [item.text for item in soup.find_all("li")]
            return info_list

        try:

            plant_dict[name]= foo("//*[@id='maincontent']/div[2]/div/div[2]/div[4]/div/ul/ul",name)


        except NoSuchElementException:
            
            try: 

                plant_dict[name] = foo("//*[@id='maincontent']/div[2]/div/div[2]/div[4]/div/ul",name)


            except NoSuchElementException:

                plant_dict[name] = ["Missing"]

        #Get the blurb and growing tips
        
        try:

            blurbandtips_elements = driver.find_elements_by_css_selector("div.value p span")


            #Unusual you could find a blurb
            if len(blurbandtips_elements) == 0:

                blurbandtips_elements = driver.find_elements_by_css_selector("div.product div.value")

            elif len(blurbandtips_elements) == 1:
                 #If no plant information
                print(type(blurbandtips_elements))
                print(len(blurbandtips_elements))
                if "Growing Tips" in blurbandtips_elements[0].text:
                    plant_dict[name] += ["Missing",blurbandtips_elements[0].text]

                #If no growing tips 
                else:
                    plant_dict[name] += [blurbandtips_elements[0].text, "Missing"]

            else:
                for element in blurbandtips_elements[:2]:
                    plant_dict[name] += [element.text]
               

        except NoSuchElementException:

            plant_dict[name] += ["Missing", "Missing"]


        #Get the sku


        try:

            sku_element = driver.find_element_by_css_selector("div.sku div.value")
            plant_dict[name] += [sku_element.text]


        except NoSuchElementException:

            plant_dict[name] += ["Missing"]

        
        #Get URL

        url = driver.current_url
        plant_dict[name] += [url]

        #Print current index and write to json in case of an error  

        print(i)
        with open("backup.json","w") as f:
            json.dump(plant_dict,f,indent="")
                
        driver.back()

        


    driver.back()


## ------ ## 

data_series = pd.Series(plant_dict)
data_list = data_series.to_list()
data_list_padded = list(zip(*itertools.zip_longest(*data_list, fillvalue=np.NaN)))

column_names = ["item" + str(number) for number in range(len(data_list_padded[0]))]
column_names[-3:] = ["Plant Information","Growing Tips","SKU"]

df = pd.DataFrame(data_list_padded,columns = column_names ,index=data_series.index)

df.to_csv("HeirloomSeeds.csv")


