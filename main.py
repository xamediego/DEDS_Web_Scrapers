import BolScraper as Bol
import AmazonScraper as Ama
import DecathlonScrapper as Deca
import asyncio


async def scrape_data_all():
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    deca_data = await Deca.start_scraper(hdr, 'jassen', 'Heren')

    print('Amazon scrape')
    amazon_data = Ama.scrape_amazon(hdr, 'jassen')

    print('Bol scrape')
    bol_data = Bol.scraper(hdr, 'jassen', 'Herenmode')

    # IDK lol
    def add_data(d1, d2):
        data = {'reviews': [], 'images': []}

        data['reviews'] = data['reviews'] + d1['reviews']
        data['images'] = data['images'] + d1['images']

        data['reviews'] = data['reviews'] + d2['reviews']
        data['images'] = data['images'] + d2['images']
        return data

    scraped_date = {'reviews': [], 'images': []}

    scraped_data_am = add_data(scraped_date, amazon_data)
    scraped_data_compl = add_data(scraped_data_am, bol_data)
    scraped_data_deca = add_data(scraped_data_am, deca_data)

    r_l = len(scraped_data_compl['reviews'])
    i_l = len(scraped_data_compl['images'])

    # Write reviews to txt
    print(f'Amount of reviews collected: {r_l}')
    print("Write reviews to txt")
    print(scraped_data_compl['reviews'])

    def write_array_to_file(arr, file_path):
        with open(file_path, 'w') as f:
            for string in arr:
                f.write(string + '\n')

    write_array_to_file(scraped_data_compl['reviews'], 'output.txt')


asyncio.run(scrape_data_all())
