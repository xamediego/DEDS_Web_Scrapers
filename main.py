import os

import requests

import BolScraper as Bol
import AmazonScraper as Ama
import DecathlonScrapper as Deca
import asyncio
from hdfs import InsecureClient


def save_images_to_folder(image_urls, folder_path):
    os.makedirs(folder_path, exist_ok=True)

    # Loop over each image URL
    for i, url in enumerate(image_urls):
        # Get the image data from the URL
        response = requests.get(url)

        # Generate a unique filename for the image
        filename = f"image_{i}.jpg"

        # Save the image to the folder
        with open(os.path.join(folder_path, filename), "wb") as f:
            f.write(response.content)

def add_data(d1, d2):
    data = {'reviews': [], 'images': []}

    data['reviews'] = data['reviews'] + d1['reviews']
    data['images'] = data['images'] + d1['images']

    data['reviews'] = data['reviews'] + d2['reviews']
    data['images'] = data['images'] + d2['images']
    return data


async def get_deca_data(hdr):
    print('Deca scrape')
    deca_data = await Deca.start_scraper(hdr, 'jassen', 'Heren')

    return deca_data


async def get_ama_data(hdr):
    print('Amazon scrape')
    amazon_data = Ama.scrape_amazon(hdr, 'jassen')

    return amazon_data


async def get_bol_data(hdr):
    print('Bol scrape')
    bol_data = Bol.scraper(hdr, 'jassen', 'Herenmode')

    return bol_data


def write_array_to_txt(array):
    def write_array_to_file(arr, file_path):
        with open(file_path, 'w') as f:
            for string in arr:
                f.write(string + '\n')

    write_array_to_file(array['reviews'], 'output.txt')

async def scrape_data_all():
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    scraped_date = {'reviews': [], 'images': []}

    # scraped_date = add_data(scraped_date, await get_ama_data(hdr))
    scraped_date = add_data(scraped_date, await get_bol_data(hdr))
    # scraped_date = add_data(scraped_date, await get_deca_data(hdr))

    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])

    # Write reviews to txt
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')
    print("Write reviews to txt")
    print(scraped_date['images'])

    folder_path = "images"

    def write_array_to_file(arr, file_path):
        with open(file_path, 'w') as f:
            for string in arr:
                f.write(string + '\n')

    write_array_to_file(scraped_date['reviews'], 'text_files/output.txt')
    save_images_to_folder(scraped_date['images'], folder_path)

    # client = InsecureClient('hdfs://localhost:9000')
    #
    # client.write('/my_dir/data.txt', data=scraped_date['reviews'], overwrite=True)

asyncio.run(scrape_data_all())


