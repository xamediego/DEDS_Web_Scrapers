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
    data = {'reviews': [], 'images': []}

    data['reviews'] = data['reviews'] + d1['reviews']
    data['images'] = data['images'] + d1['images']

    data['reviews'] = data['reviews'] + d2['reviews']
    data['images'] = data['images'] + d2['images']
    return data


def write_array_to_file(arr, file_path):
    with open(file_path, 'w') as f:
        for string in arr:
            f.write(string + '\n')