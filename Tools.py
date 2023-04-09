import csv
import os
import requests
from selenium.common import TimeoutException


def save_images_to_folder(image_urls, folder_path):
    os.makedirs(folder_path, exist_ok=True)

    # Loop over each image URL
    for i, url in enumerate(image_urls):
        if url is not None:
            # Get the image data from the URL
            response = requests.get(url)

            # Generate a unique filename for the image
            filename = f"image_{i}.jpg"

            # Save the image to the folder
            with open(os.path.join(folder_path, filename), "wb") as f:
                f.write(response.content)


def add_data(d1, d2):
    print('ADD')
    get_scraped_data_size_info(d2)
    print('ADD TO')
    get_scraped_data_size_info(d1)
    d1['reviews'] = d1['reviews'] + d2['reviews']
    d1['images'] = d1['images'] + d2['images']
    d1['prices'] = d1['prices'] + d2['prices']
    d1['titles'] = d1['titles'] + d2['titles']
    print('ADDED TO TOTAL')
    get_scraped_data_size_info(d1)


def get_scraped_data_size_info(scraped_date):
    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])
    p_l = len(scraped_date['prices'])
    t_l = len(scraped_date['titles'])
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')
    print(f'Amount of prices collected: {p_l}')
    print(f'Amount of titles collected: {t_l}')


def write_csv(data, filename):
    # Open the CSV file for writing in UTF-8 encoding
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)

        # Write each item in the data array to a separate row in the CSV file
        for row in data:
            writer.writerow(row)


def remove_unicode(data):
    # Create a new array to store the cleaned data
    cleaned_data = []

    # Loop over each item in the data array
    for row in data:
        # Split the row into individual words
        words = row.split()

        # Convert each word to ASCII encoding
        cleaned_words = [word.encode('ascii', 'ignore').decode('ascii') for word in words]

        # Join the cleaned words back together with spaces
        cleaned_row = ' '.join(cleaned_words)

        # Add the cleaned row to the cleaned data array
        cleaned_data.append(cleaned_row)

    # Return the cleaned data array
    return cleaned_data


def write_array_to_file(arr, file_path):
    with open(file_path, 'w') as file:
        # Write each row of data to the text file
        for row in arr:
            if row is not None:
                file.write(row + '\n')


def clear_folder(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            os.rmdir(item_path)


def load_page(driver, link, load_time):
    driver.set_page_load_timeout(load_time)

    try:
        driver.get(link)
        # continue with the next steps
    except TimeoutException as e:
        print("Page load Timeout Occurred. Refreshing !!!")
        print(link)
        driver.refresh()


def copy_strings(array):
    new_array = []
    for string in array:
        words = string.split()
        if len(words) >= 100:
            new_array.append(string)
    return new_array

def copy_floats(array):
    new_array = []
    for string in array:
        try:
            float_val = float(string.replace(',', '.'))
            new_array.append(float_val)
        except ValueError:
            pass
    return new_array