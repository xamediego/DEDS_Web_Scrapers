import Tools
import BolScraper as Bol
import AmazonScraper as Ama
import DecathlonScrapper as Deca
import asyncio
from hdfs import InsecureClient


async def scrape_data_all():
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    scraped_date = {'reviews': [], 'images': []}

    scraped_date = Tools.add_data(scraped_date, await Ama.get_ama_data(hdr, 'jassen'))
    scraped_date = Tools.add_data(scraped_date, await Bol.get_bol_data(hdr, 'jassen', 'Herenmode'))
    scraped_date = Tools.add_data(scraped_date, await Deca.get_deca_data(hdr, 'jassen', 'Heren'))

    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])

    # Write reviews to txt
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')
    print("Write reviews to txt")
    print(scraped_date['images'])

    folder_path = "images"

    Tools.write_array_to_file(scraped_date['reviews'], 'text_files/output.txt')
    Tools.save_images_to_folder(scraped_date['images'], folder_path)

    # client = InsecureClient('hdfs://localhost:9000')
    #
    # client.write('/my_dir/data.txt', data=scraped_date['reviews'], overwrite=True)


asyncio.run(scrape_data_all())
