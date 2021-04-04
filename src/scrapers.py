import requests
from bs4 import Tag, NavigableString, BeautifulSoup
import re
import json
import pandas as pd
import time

class CompetitorScraper():
    
    def __init__(self):
        self.url = "https://muebleslufe.com"
        self.df_data = pd.DataFrame(data=None,columns=['Title', 'Price', 'Rating', 'Qty_Opiniones','Medidas_JSON_format','Image_Url', 'Item_Url'],index=['Item_Url'])

    def bs_parse(self, html):
        return BeautifulSoup(html, 'lxml')

    def download(self, url, num_retries=2, user_agent='wswp'):
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
        url = self.download(self.url)
        soup = self.bs_parse(url)
        a_tags = soup.body.find_all('a')
        pattern=re.compile('{0}/es/[0-9]+-'.format(self.url))
        return {link.get('href') for link in a_tags if re.match(pattern, str(link.get('href')))}
    
    def get_items_links(self, category_page):
        url = self.download(category_page)
        soup = self.bs_parse(url)
        a_tags = soup.body.find_all('a')
        pattern=re.compile('{0}/es/[\w-]+/[0-9]+-[\w-]*.html'.format(self.url))
        return {link.get('href') for link in a_tags if re.match(pattern, str(link.get('href')))}
    
    def get_features(self, item_page):
        url = self.download(item_page)
        soup = self.bs_parse(url)
        item_dict = dict()
        if not soup.body.find('div', {'class':"pagenotfound"}):    
            
            # Getting tittle and price
            title = soup.body.find(itemprop="name").string
            price = soup.body.find(id="our_price_display").attrs['content'] # Another option to get the price => {tag.get('content') for tag in soup.body.find_all('span') if tag.get('content') and tag.get('itemprop')=="price"}
            item_dict["Title"]=[title]
            item_dict["Price"]=[price]
            
            # Getting Rating
            resultset=soup.body.find_all('p',{"class":"netreviews_note_generale"})
            if len(resultset) != 0: 
                rating=next(resultset[0].children).split()[0]
                item_dict["Rating"]=[rating]
                # Getting the amount of opinions
                qty_opiniones = soup.body.find(id="reviewCount").string
                item_dict["Qty_Opiniones"]=[qty_opiniones]
            else:
                item_dict["Rating"]=[None]
                item_dict["Qty_Opiniones"]=[None]
                
            # Getting features            
            try:
                temp_dict = dict()
                medidas = soup.body.find(id="extraTab_2").contents                 
                for content in range(len(medidas)):
                    tag_list = []
                    string_list = []
                    for element in medidas[content].contents:
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

                medidas_json = json.dumps(temp_dict, ensure_ascii=False)   
                item_dict["Medidas_JSON_format"]= [medidas_json]          
            except:
                item_dict["Medidas_JSON_format"]=[None]            
            
            # Getting image url
            item_dict["Image_Url"]=[soup.body.find_all('img', {'itemprop':"image"})[0].attrs['src']]
            # Getting the item url
            item_dict["Item_Url"]=[item_page]    
            
        return item_dict
    
    def scrape(self):    
        for cat_link in self.get_category_links():
            for item_link in self.get_items_links(cat_link):
                self.df_data = self.df_data.append(pd.DataFrame(self.get_features(item_link)))
                time.sleep(2)
            time.sleep(3)        
    
    def data2csv(self, filename):
        # Overwrite to the specified file.
        # Create it if it does not exist.
        self.df_data.to_csv(filename, sep=';', index=False, encoding = 'latin')

