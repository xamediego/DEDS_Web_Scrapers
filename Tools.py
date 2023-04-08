import csv
import os
import requests


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
    data = {'reviews': d1['reviews'] + d2['reviews'], 'images': d1['images'] + d2['images'],
            'prices': d1['prices'] + d2['prices']}

    return data


def get_scraped_data_size_info(scraped_date):
    r_l = len(scraped_date['reviews'])
    i_l = len(scraped_date['images'])
    p_l = len(scraped_date['prices'])
    print(f'Amount of reviews collected: {r_l}')
    print(f'Amount of images collected: {i_l}')
    print(f'Amount of prices collected: {p_l}')


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
            file.write(row + '\n')


def clear_folder(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            os.rmdir(item_path)