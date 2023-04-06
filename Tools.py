import csv
import os
from hdfs import InsecureClient
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

    data['reviews'] = d1['reviews'] + d2['reviews']
    data['images'] = d1['images'] + d2['images']

    return data


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


def write_to_hdsf(data):
    DOCKER_NETWORK = 'docker-hadoop-master_default'
    ENV_FILE = 'hadoop.env'

    client = InsecureClient('http://localhost:9870', user='root')

    # Make a new directory in HDFS
    client.makedirs('/input')

    directories = client.list('/')
    print(directories)

    client = InsecureClient('http://localhost:9870', user='root')

    # Upload the local file to the Hadoop cluster
    client.upload('/input/example.txt', 'input/example.txt', overwrite=True)

    # Run the Docker image
    os.system(f'docker run --network {DOCKER_NETWORK} --env-file {ENV_FILE} hadoop-wordcount')

    # Print the output of the Hadoop job
    with client.read('/output/part-r-00000', encoding='utf-8') as reader:
        print(reader.read())

    # Remove the output and input directories from HDFS
    client.delete('/output', recursive=True)
    client.delete('/input', recursive=True)

