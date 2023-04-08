import Tools
import MakeTool
from scrapers import Bol_Sel as Bs, AmazonScraper as Ama, Deca_Scraper as Deca, Adidas_Scraper as Adi, \
    Bever_Scraper as Bever


def scrape_data_all():
    scraped_date = {'reviews': [], 'images': [], 'prices': []}

    search_term = 'jassen'

    scraped_date = Tools.add_data(scraped_date, Bever.scrape_full(search_term, 1))
    Tools.get_scraped_data_size_info(scraped_date)

    scraped_date = Tools.add_data(scraped_date, Adi.scrape_full(search_term, 1))
    Tools.get_scraped_data_size_info(scraped_date)

    scraped_date = Tools.add_data(scraped_date, Ama.scrape_full(search_term, 1))
    Tools.get_scraped_data_size_info(scraped_date)

    scraped_date = Tools.add_data(scraped_date, Bs.scrape_full(search_term, 'Herenmode', 1))
    Tools.get_scraped_data_size_info(scraped_date)

    scraped_date = Tools.add_data(scraped_date, Deca.scrape_full(search_term, 1, 1))
    Tools.get_scraped_data_size_info(scraped_date)

    data = scraped_date['reviews']
    cleaned_data = Tools.remove_unicode(data)

    print("Write reviews to txt and save images")
    save_data(cleaned_data, scraped_date['images'], scraped_date['prices'])

    print("Upload stuff to hadoop")
    upload_to_hadoop()


def clear_image_folder():
    source_path_images = "submit/images"

    Tools.clear_folder(source_path_images)
def save_data(cleaned_reviews, images, cleaned_prices):
    folder_path_review = "submit/reviews/textbestand.txt"
    folder_path_prices = "submit/prices/textbestand.txt"
    folder_path_image_links = "submit/image_links/textbestand.txt"
    folder_path_images = "submit/images/"

    Tools.write_array_to_file(cleaned_reviews, folder_path_review)
    Tools.write_array_to_file(cleaned_prices, folder_path_prices)
    Tools.write_array_to_file(images, folder_path_image_links)
    Tools.save_images_to_folder(images, folder_path_images)


def upload_to_hadoop():
    source_path_review = "submit/reviews/."
    source_path_prices = "submit/prices/."
    source_path_images = "submit/images/."

    des_path_review = "/input/reviews/"
    des_path_prices = "/input/prices/"
    des_path_images = "/input/images/"

    MakeTool.upload(source_path_review, des_path_review)
    MakeTool.upload(source_path_prices, des_path_prices)
    MakeTool.upload(source_path_images, des_path_images)

    clear_image_folder()

scrape_data_all()

