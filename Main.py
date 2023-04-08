import time

import Tools
import MakeTool
import threading

from scrapers import Bol_Sel as Bs, AmazonScraper as Ama, Deca_Scraper as Deca, Adidas_Scraper as Adi, \
    Bever_Scraper as Bever


def scrape_data_all():
    scraped_date = {'reviews': [], 'images': [], 'prices': []}
    print(scraped_date['images'])
    search_term = 'jassen'

    # Define a function to run each scraper in a thread
    def run_scraper(scraper_func, *args):
        result = scraper_func(*args)
        Tools.add_data(scraped_date, result)

    # Create a thread for each scraper
    bever_thread = threading.Thread(target=run_scraper, args=(Bever.scrape_full, search_term, 1))
    adidas_thread = threading.Thread(target=run_scraper, args=(Adi.scrape_full, search_term, 1))
    amazon_thread = threading.Thread(target=run_scraper, args=(Ama.scrape_full, search_term, 1))
    bol_thread = threading.Thread(target=run_scraper, args=(Bs.scrape_full, search_term, 'Herenmode', 1))
    deca_thread = threading.Thread(target=run_scraper, args=(Deca.scrape_full, search_term, 1, 1))

    # Start all threads
    # bever_thread.start()
    time.sleep(5)
    adidas_thread.start()
    time.sleep(5)
    # amazon_thread.start()
    time.sleep(5)
    # bol_thread.start()
    time.sleep(5)
    # deca_thread.start()


    # Wait for all threads to complete
    # bever_thread.join()
    adidas_thread.join()
    # amazon_thread.join()
    # bol_thread.join()
    # deca_thread.join()

    data = scraped_date['reviews']
    cleaned_data = Tools.remove_unicode(data)

    print(scraped_date['images'])
    test(scraped_date['images'])
    # print("Write reviews to txt and save images")
    save_data(cleaned_data, scraped_date['images'], scraped_date['prices'])

    # print("Upload stuff to hadoop")
    # upload_to_hadoop()


def clear_image_folder():
    source_path_images = "submit/images"

    Tools.clear_folder(source_path_images)


def save_data(cleaned_reviews, images, cleaned_prices):
    folder_path_review = "submit/reviews/textbestand.txt"
    folder_path_prices = "submit/prices/textbestand.txt"
    folder_path_image_links = "submit/image_links/textbestand.txt"

    image_links = images.copy()

    Tools.write_array_to_file(cleaned_reviews, folder_path_review)
    Tools.write_array_to_file(cleaned_prices, folder_path_prices)
    Tools.write_array_to_file(image_links, folder_path_image_links)



def test(images):
    folder_path_images = "submit/images/"
    Tools.save_images_to_folder(images, folder_path_images)
    print('IMAGES SHOULD BE SAVED')


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
