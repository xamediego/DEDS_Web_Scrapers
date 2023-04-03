import BolScraper as Bol

scraped_data = Bol.bol_scraper('jassen', 'Herenmode')

r_l = len(scraped_data['reviews'])
i_l = len(scraped_data['images'])

# Write reviews to txt
print(f'Amount of reviews collected: {r_l}')
print("Write reviews to txt")
print(scraped_data['reviews'])
