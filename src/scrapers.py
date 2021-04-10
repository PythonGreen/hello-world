import requests
from bs4 import Tag, NavigableString, BeautifulSoup
import re
import json
import pandas as pd
import time

class CompetitorScraper():
    
    def __init__(self):
        # initializing url to scrape and pandas dataframe that will be used to keep the data scraped
        self.url = "https://muebleslufe.com"
        self.df_data = pd.DataFrame(data=None,columns=['Title', 'Price', 'Category_path', 'Rating', 'Qty_califications','Features_JSON_format','Image_Url', 'Item_Url'])
        self.df_data_raw = pd.DataFrame(data=None,columns=['Title', 'Price', 'Category_path', 'Rating', 'Qty_califications','Features_JSON_format','Image_Url', 'Item_Url'])

    def bs_parse(self, html):
        return BeautifulSoup(html, 'lxml')

    def download(self, url, num_retries=2, user_agent='wswp'):
        # with this method it is possible to get the html content of an url
        print('Downloading:', url)
        headers = {'User-agent': user_agent}
        try:
            html = requests.get(url, headers=headers)
        except (URLError, HTTPError, ContentTooShortError) as e:
            print('Download error:', e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return download(url, num_retries - 1)                
        return html.content

    def get_category_links(self):
        # through this method you can get all posible category url of the competitor web site.
        # All URLs are returned in a set object in order to get 1 on the n possible repeated category URLs
        # Using an regex we can retrieve valid category URLs.
        url = self.download(self.url)
        soup = self.bs_parse(url)
        a_tags = soup.body.find_all('a')
        pattern=re.compile('{0}/es/[0-9]+-'.format(self.url))
        return {link.get('href') for link in a_tags if re.match(pattern, str(link.get('href')))}
    
    def get_items_links(self, category_page):
        # by passing through the category url to this method you can get a set with all item URLs published within the category
        # Using an regex we can retrieve valid item URLs.
        url = self.download(category_page)
        soup = self.bs_parse(url)
        a_tags = soup.body.find_all('a')
        pattern=re.compile('{0}/es/[\w-]+/[0-9]+-[\w-]*.html'.format(self.url))
        return {link.get('href') for link in a_tags if re.match(pattern, str(link.get('href')))}
    
    def get_features(self, item_page):
        # with the get_features method we can get all the fields needed for the item url passed by parameter.
        # All of them are saved in a dictionary object
        url = self.download(item_page)
        soup = self.bs_parse(url)
        item_dict = dict()
        if not soup.body.find('div', {'class':"pagenotfound"}):    
            
            # Getting tittle and price
            title = soup.body.find(itemprop="name").string
            price = soup.body.find(id="our_price_display").attrs['content'] # Another option to get the price => {tag.get('content') for tag in soup.body.find_all('span') if tag.get('content') and tag.get('itemprop')=="price"}
            item_dict["Title"]=[title]
            item_dict["Price"]=[price]
            
            # Getting Category path
            category_path = ''
            for tag in soup.body.find('div', {'class':"breadcrumb"}):
                category_path += tag.string
            item_dict["Category_path"]=[re.sub('[\t\n]+','',category_path)] 

            # Getting Rating
            resultset=soup.body.find_all('p',{"class":"netreviews_note_generale"})
            if len(resultset) != 0: 
                rating=next(resultset[0].children).split()[0]
                item_dict["Rating"]=[rating]
                # Getting the amount of opinions
                qty_califications = soup.body.find(id="reviewCount").string
                item_dict["Qty_califications"]=[qty_califications]
            else:
                item_dict["Rating"]=[None]
                item_dict["Qty_califications"]=[None]
                
            # Getting features
            # In order to get all the features of an item we take into account all posibles combinatios:
            # - Products without features
            # - Product with measures and/or the material made of
            # - Publications where you have measures of two products, for example tables and chairs
            # - etcetera...
            try:
                temp_dict = dict()
                features = soup.body.find(id="extraTab_2").contents                 
                for content in range(len(features)):
                    tag_list = []
                    string_list = []
                    for element in features[content].contents:
                        if isinstance(element, Tag) and element.string is not None:
                            tag_list.append(element.string)
                        if isinstance(element, NavigableString):
                            string_list.append(element.string)


                    if len(tag_list) == len(string_list):
                        tag_list = [elem.replace(':','') for elem in tag_list]
                        temp_dict = dict(zip(tag_list,string_list))
                    else:
                        try: 
                            tag_list[0] = 'Descripcion: ' + tag_list[0]
                        except:
                            pass
                        total_list = tag_list + string_list
                        header_list = [elem.split(':')[0]+'_'+str(content) for elem in total_list]             
                        try:
                            body_list = [elem.split(':')[1] for elem in total_list]
                        except:
                            body_list = [None]
                        temp_dict.update(dict(zip(header_list, body_list)))

                features_json = json.dumps(temp_dict, ensure_ascii=False)   
                item_dict["Features_JSON_format"]= [features_json]          
            except:
                item_dict["Features_JSON_format"]=[None]            
            
            # Getting image url
            item_dict["Image_Url"]=[soup.body.find_all('img', {'itemprop':"image"})[0].attrs['src']]
            # Getting the item url
            item_dict["Item_Url"]=[item_page]    
            
        return item_dict
    
    def scrape(self):
        # this is the main method where you initiate the scraping process and get as result 
        # both class pandas dataframes loaded with all Competitor data.
        for cat_link in self.get_category_links():
            for item_link in self.get_items_links(cat_link):
                self.df_data_raw = self.df_data_raw.append(pd.DataFrame(self.get_features(item_link)))
                time.sleep(2)
            time.sleep(3)
        self.df_data = self.df_data_raw.drop_duplicates()
    
    def data2csv(self, filename):
        # Overwrite to the specified file.
        # Create it if it does not exist.
        self.df_data.to_csv(filename, sep=';', index=False, encoding = 'latin')

