import Tools
import AmazonScraper as Ama
import DecathlonScrapper as Deca
import asyncio
from hdfs import InsecureClient
import Bol_Sel as Bs


async def scrape_data_all():
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    scraped_date = {'reviews': [], 'images': []}

    scraped_date = Tools.add_data(scraped_date, await Ama.get_ama_data('jassen'))

    scraped_date = Tools.add_data(scraped_date, await Bs.get_bol_data('jassen', 'Herenmode'))

    scraped_date = Tools.add_data(scraped_date, await Deca.get_deca_data(hdr, 'jassen', 'Heren'))

    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')

    # Write reviews to txt
    print("Write reviews to txt")

    # Define the data to be cleaned
    data = scraped_date['reviews']

    # Call the remove_unicode function to clean the data
    cleaned_data = Tools.remove_unicode(data)

    folder_path = "images"

    # Tools.write_array_to_file(cleaned_data, 'text_files/output.txt')
    Tools.save_images_to_folder(scraped_date['images'], folder_path)

    # Tools.write_to_hdsf(scraped_date['reviews'])

    # client = InsecureClient('hdfs://localhost:9000')
    #
    # client.write('/my_dir/data.txt', data=scraped_date['reviews'], overwrite=True)


asyncio.run(scrape_data_all())

# def test_hsdf():
#     data = ['Prima jas voor een lage prijs.', 'Goede pasvorm heel licht en aangenaam om te dragen.',
#             'Snelle reactie, snelle levering, perfect afhandeling, precies zoals ik het verwachte.']
#
#     # Call the remove_unicode function to clean the data
#     cleaned_data = Tools.remove_unicode(data)
#
#     # Open the text file for writing
#     with open('input/example.txt', 'w') as file:
#         # Write each row of cleaned data to the text file
#         for row in cleaned_data:
#             file.write(row + '\n')
#
#     print('WRITE TO HDSF')
#     Tools.write_to_hdsf(cleaned_data)
#
#
# test_hsdf()
