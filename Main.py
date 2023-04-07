import Tools
import MakeTool
import asyncio
from scrapers import Bol_Sel as Bs, AmazonScraper as Ama, Deca_Scraper as Deca, Adidas_Scraper as Adi


async def scrape_data_all():
    scraped_date = {'reviews': [], 'images': []}

    scraped_date = Tools.add_data(scraped_date, Adi.get_adi_data('jassen'))
    get_scraped_data_size_info(scraped_date)

    # scraped_date = Tools.add_data(scraped_date, await Ama.get_ama_data('jassen'))
    # get_scraped_data_size_info(scraped_date)

    # scraped_date = Tools.add_data(scraped_date, await Bs.get_bol_data('jassen', 'Herenmode'))
    # get_scraped_data_size_info(scraped_date)

    # scraped_date = Tools.add_data(scraped_date, await Deca.get_deca_data('jassen'))
    # get_scraped_data_size_info(scraped_date)

    # get_scraped_data_size_info(scraped_date)
    #
    # data = scraped_date['reviews']
    # cleaned_data = Tools.remove_unicode(data)
    #
    # print("Write reviews to txt and save images")
    # save_data(cleaned_data, scraped_date['images'])
    #
    # print("Upload stuff to hadoop")
    # upload_to_hadoop()


def get_scraped_data_size_info(scraped_date):
    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')

def save_data(cleaned_reviews, images):
    folder_path_review = "submit/reviews/textbestand.txt"
    folder_path_images = "submit/images/"

    Tools.write_array_to_file(cleaned_reviews, folder_path_review)
    Tools.save_images_to_folder(images, folder_path_images)


def upload_to_hadoop():
    source_path_review = "submit/reviews/."
    source_path_images = "submit/images/."

    des_path_review = "/input/reviews/"
    des_path_images = "/input/images/"

    MakeTool.upload(source_path_review, des_path_review)
    MakeTool.upload(source_path_images, des_path_images)


asyncio.run(scrape_data_all())

# upload_to_hadoop()