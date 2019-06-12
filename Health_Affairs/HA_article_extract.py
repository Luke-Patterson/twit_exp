# extract articles from HA website
import pandas as pd
import numpy as np
import pycountry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
# load excel file of classifications
df = pd.read_excel('input/HA to IMPAQ Category Classification clean.xlsx')
# convert categories/keywords to lists
for i in ['HA Category', 'Keywords']:
    df[i] = df[i].str.split(", ")

# start chrome webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    "C:/Users/lpatterson/AnacondaProjects/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)

kword_df = pd.DataFrame(columns=['IMPAQ Category','Keyword','Title','Authors',
    'Publication Date','Type','Tag','Link'])
# iterate through the different categories for HA articles
for iter in df.iterrows():
    row = iter[1]
    print('extracting articles for IMPAQ Category ' + row['IMPAQ Category'])
    cat = row['IMPAQ Category']
    ha_cat = row['HA Category']
    kwords = row['Keywords']
    # look up search results for each keyword
    for kword in kwords:
        print('extracting articles for keyword ' + kword)
        kword = kword.strip()
        # open/setup the search parameters for HA advanced search
        driver.get('https://www.healthaffairs.org/search/advanced')
        sleep(.5)
        # change to just title search
        driver.find_element_by_xpath("//*[@class='jcf-select jcf-unselectable"
            + " jcf-select-jcf']").click()
        driver.find_element_by_xpath("//*[@data-index='1']").click()
        # enter keyword
        driver.find_element_by_xpath("//*[@placeholder='Enter Search term']") \
            .send_keys(kword)
        # go back to 2010 - when HA first started tweeting
        driver.find_element_by_xpath("//*[@for='customRange']").click()
        driver.find_element_by_xpath("//*[@class='jcf-select jcf-unselectable"
        + " jcf-select-inline jcf-select-year-range jcf-select-jcf']//*[@class="
        + "'jcf-select-text']").click()
        driver.find_element_by_xpath("//*[@data-index='11']").click()
        # click search
        driver.find_element_by_xpath("//*[@id='advanced-search-btn']").click()
        # result page should now pop up
        sleep(.5)
        driver.maximize_window()
        # expand to 100 results per page if present
        try:
            driver.find_element_by_xpath('//*[@id="pb-page-content"]/div/main/div[2]'
            + '/div/div[1]/div/div[3]/div[1]/div[2]/div[1]/ul/li[3]/a').click()
            # record each result as a row in kword_df
            print(str(len(driver.find_elements_by_class_name('item__body')))+ ' articles found')
            for i, article in enumerate(driver.find_elements_by_class_name('item__body')):
                kword_row = pd.Series(index=['IMPAQ Category','Keyword','Title',
                    'Authors','Publication Date','Type','Tag','Link'])
                kword_row['IMPAQ Category'] = cat
                kword_row['Keyword'] = kword
                # title of article
                kword_row['Title'] = article.find_element_by_class_name('item__title').text
                # authors
                kword_row['Authors'] =article.find_elements_by_xpath("//*[@class='rlist--"
                    +"inline loa']")[i].text
                # publication date
                kword_row['Publication Date'] = article.find_element_by_class_name(
                    'item__detail').text
                if 'Open Access' in kword_row['Publication Date']:
                    kword_row['Publication Date'] = kword_row['Publication Date'] \
                        .replace('Open Access','')
                if 'Free Access' in kword_row['Publication Date']:
                    kword_row['Publication Date'] = kword_row['Publication Date'] \
                        .replace('Free Access','')
                # type of article
                kword_row['Type'] = article.find_elements_by_xpath(
                "//*[@class='meta__header']//*[@class='filled--journal default']")[i].text
                # topic tag - not always present
                try:
                    kword_row['Tag'] = article.find_elements_by_xpath("//*[@class='"
                        +"journal-label']")[i].text
                except:
                    kword_row['Tag'] = None
                # Link to article
                kword_row['Link'] = article.find_element_by_xpath('.//*[@class="item__title"]/a') \
                    .get_attribute("href")
                kword_df = kword_df.append(kword_row, ignore_index = True, sort = False)
        except:
            continue
kword_df = kword_df.drop_duplicates(['IMPAQ Category','Title'])

# search in title didn't work, let's see how many we'd get with strictly enforcing that
titles = kword_df.Title.str.lower()
kwords = kword_df.Keyword
compare_df =pd.Dataframe([titles, kwords]).transpose()
def compare_strings(words, in_str):
    all_words = True
    for i in words.split():
        if i not in in_str:
            all_words = False
    return(all_words)

compare_df['Result']=False
for i,row in compare_df.iterrows():
    compare_df.loc[i,'Result'] = compare_strings(row['Keyword'],row['Title'])

kword_df = kword_df.reset_index(drop=True)
kword_df.to_csv('output/HA_articles.csv')
