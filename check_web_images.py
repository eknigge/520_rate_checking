import os
from google.cloud import vision
import io
import re
import urllib
import logging
import datetime
import time
import TollData as td
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_vision_text(image_filename: str) -> str:
    logging.debug(f'vision image filename: {image_filename}')
    client = vision.ImageAnnotatorClient()

    with io.open(image_filename, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations

    output = []
    for text in texts:
        description = str(text.description).replace('\n', '')
        logging.debug(f'Text to search: {description}')
        match_pattern = '\d\.\d{2}'
        matches = re.findall(match_pattern, description)
        output += matches

        # include alt matching pattern, and matches
        alt_pattern = '\d{3}'
        alt_matches = re.findall(alt_pattern, description)
        output += alt_matches

    # convert elements to float
    for i in range(len(output)):
        output[i] = float(output[i])
    
    # convert large values to small ones
    for value in output:
        if value > 10:
            output.append(value/100.00)

    return output


def initialize_logging():
    now = datetime.datetime.now()
    start_time = f'{now.year}{now.month}{now.day}_{now.hour}{now.minute}{now.second}'
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', filename=f'{start_time}_vision_process.log',
                        level=logging.DEBUG)


# move files into an image archive folder
def archive_images():
    archive = 'image_archive'
    files = os.listdir(os.getcwd())
    image_files = [i for i in files if 'jpg' in i]
    cwd = os.getcwd()

    if archive not in files:
        logging.debug(f'Create archive directory {archive}')
        os.mkdir(archive)

    for image in image_files:
        logging.debug(f'Archiving File: {image}')
        dir_format = '\\'
        if os.name != 'nt':
            dir_format = '/'
        os.replace(cwd+dir_format+image, cwd+dir_format+archive+dir_format+image)


def download_filename_images(urls: dict) -> dict:
    now = datetime.datetime.now()
    time_text = f'{now.year}{now.month}{now.day}_{now.hour}{now.minute}_'
    for direction in urls:
        output_filename = f'{time_text}_{direction}.jpg'
        logging.debug(f'Output filename: {output_filename}')
        urls[direction][1] = output_filename
        urllib.request.urlretrieve(urls[direction][0], output_filename)
        logging.debug(f'Downloaded {direction} image and saved as {output_filename}')
    return urls


def main():
    initialize_logging()
    end_time = datetime.datetime(2022, 8, 17)
    image_download_interval_secs = 60*15
    urls = {
        'east': ['img_url', 'img_output_filename', 'ai_text'],
        'west': ['img_url', 'img_output_filename', 'ai_text']
    }
    urls['east'][0] = 'https://images.wsdot.wa.gov/nw/520vc00414.jpg'
    urls['west'][0] = 'https://images.wsdot.wa.gov/nw/520vc00430.jpg'
    logging.debug(f"West URL: {urls['west']}")
    logging.debug(f"East URL: {urls['east']}")

    while datetime.datetime.now() < end_time:
        logging.debug('While loop iteration start')
        urls = download_filename_images(urls)

        # get expected toll rate
        now = datetime.datetime.now()
        expected_rate = float(td.AssignRate(now, 'AVI', 2, 'V').get_final_rate())
        logging.info(f'Expected Toll Rate: {expected_rate}')

        # get Google vision text
        for direction in urls:
            urls[direction][2] = get_vision_text(urls[direction][1])

        # compare Google vision to expected rate
        for direction in urls:
            values = urls[direction][2]

            # avi rate check
            avi_found = expected_rate in values
            logging.info(f'{direction}. AVI Rates Match: {avi_found}.'
                         f' Expected: {expected_rate}. OCR Rate(s) {values}'
                         )

            # pay by mail rate check
            pbm_found = (expected_rate+2.00) in values
            logging.info(f'{direction}. PBM Rates Match: {pbm_found}.'
                         f' Expected: {expected_rate+2.00}. OCR Rate(s) {values}'
                         )

        # move files to archive folder
        archive_images()

        # wait
        logging.debug(f'pause for {image_download_interval_secs} seconds')
        time.sleep(image_download_interval_secs)
    logging.debug('End time reached, script terminating')


if __name__ == '__main__':
    main()
