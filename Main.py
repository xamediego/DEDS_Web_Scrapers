import time

import Tools
import DockerTool
import threading

from scrapers import Bol_Sel as Bs, AmazonScraper as Ama, Deca_Scraper as Deca, Adidas_Scraper as Adi, \
    Bever_Scraper as Bever


def scrape_data_all():
    scraped_date = {'reviews': [], 'images': [], 'prices': [], 'titles': []}
    print(scraped_date['images'])
    search_term = 'jassen'

    # Define a function to run each scraper in a thread
    def run_scraper(scraper_func, *args):
        result = scraper_func(*args)
        Tools.add_data(scraped_date, result)

    # Create a thread for each scraper
    bever_thread = threading.Thread(target=run_scraper, args=(Bever.scrape_full, search_term, 1))
    adidas_thread = threading.Thread(target=run_scraper, args=(Adi.scrape_full, search_term, 1))
    amazon_thread = threading.Thread(target=run_scraper, args=(Ama.scrape_full, search_term, 1, 1))
    bol_thread = threading.Thread(target=run_scraper, args=(Bs.scrape_full, search_term, 'Herenmode', 1))
    deca_thread = threading.Thread(target=run_scraper, args=(Deca.scrape_full, search_term, 1, 1))

    # # Start all threads
    bever_thread.start()
    time.sleep(5)
    adidas_thread.start()
    time.sleep(5)
    amazon_thread.start()
    time.sleep(5)
    bol_thread.start()
    time.sleep(5)
    deca_thread.start()

    # Wait for all threads to complete
    bever_thread.join()
    adidas_thread.join()
    amazon_thread.join()
    bol_thread.join()
    deca_thread.join()

    data = scraped_date['reviews']
    cleaned_reviews = Tools.remove_unicode(data)

    cleaned_reviews_100 = Tools.copy_strings(cleaned_reviews)
    print('REVIEWS > 100: ' + str(len(cleaned_reviews_100)))

    data = scraped_date['prices']
    cleaned_prices = Tools.remove_unicode(data)
    cleaned_prices = Tools.copy_floats(cleaned_prices)

    # print("Write reviews to txt and save images")
    save_data(cleaned_reviews, cleaned_reviews_100, scraped_date['images'], scraped_date['titles'], cleaned_prices)
    download_images(scraped_date['images'])

    # print("Upload stuff to hadoop")
    upload_to_hadoop()


def clear_image_folder():
    source_path_images = "submit/images"

    Tools.clear_folder(source_path_images)


def save_data(cleaned_reviews, cleaned_reviews_100, images, titles, cleaned_prices):
    folder_path_review = "submit/reviews/reviews.txt"
    folder_path_review100 = "submit/reviews/reviews_100.txt"
    folder_path_prices = "submit/prices/prices.txt"
    folder_path_titles = "submit/titles/titles.txt"
    folder_path_image_links = "submit/image_links/image_links.txt"

    Tools.write_array_to_file(cleaned_reviews, folder_path_review)
    Tools.write_array_to_file(cleaned_reviews_100, folder_path_review100)
    Tools.write_array_to_file(cleaned_prices, folder_path_prices)
    Tools.write_array_to_file(titles, folder_path_titles)
    Tools.write_array_to_file(images, folder_path_image_links)


def download_images(images):
    folder_path_images = "submit/images/"
    Tools.save_images_to_folder(images, folder_path_images)
    print('IMAGES SHOULD BE SAVED')


def upload_to_hadoop():
    source_path_review = "submit/reviews/."
    source_path_prices = "submit/prices/."
    source_path_images = "submit/images/."
    source_path_titles = "submit/titles/."

    des_path_review = "/input/reviews/"
    des_path_prices = "/input/prices/"
    des_path_images = "/input/images/"
    des_path_titles = "/input/titles/"

    DockerTool.upload(source_path_review, des_path_review)
    DockerTool.upload(source_path_prices, des_path_prices)
    DockerTool.upload(source_path_images, des_path_images)
    DockerTool.upload(source_path_titles, des_path_titles)

    clear_image_folder()


scrape_data_all()
