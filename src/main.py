from scrapers import CompetitorScraper
import time

output_file = 'competitors_raw_data.csv'
scraper = CompetitorScraper()

start_time = time.time()
scraper.scrape()
scraper.data2csv(output_file)
end_time = time.time()
print ('\nelapsed time: {} minutes'.format(str(round(((end_time - start_time) / 60) , 2))) )