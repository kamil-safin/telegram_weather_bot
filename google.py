from bs4 import BeautifulSoup
import urllib.request as urllib
import json
import os
import sys


def get_soup(url, header):
    request = urllib.Request(url, headers=header)
    return BeautifulSoup(urllib.urlopen(request), "html.parser")


def google_image(query, max_images_needed=1):
    google_images_url_format =\
        "https://www.google.ru/search?q={}&source=lnms&tbm=isch"
    image_name = 'image'
    query = query.split()
    query = '+'.join(query)
    url = google_images_url_format.format(query)
    print("Google images url: ", url, file=sys.stderr)

    # add the directory for your image here
    dir_path = "./images/"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    header = {'User-Agent':
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 " +
              "(KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    soup = get_soup(url, header)

    # contains the link for large original images, type of image
    images = []
    for image_tag in soup.find_all("div", {"class": "rg_meta"})[:10]:
        link, image_type =\
            json.loads(image_tag.text)["ou"], json.loads(image_tag.text)["ity"]
        images.append((link, image_type))

    succeeded_images_counter = 0
    for i, (image, image_type) in enumerate(images):
        try:
            request = urllib.Request(image, headers=header)
            raw_image = urllib.urlopen(request)
            raw_image = raw_image.read()
            with open(dir_path + image_name + "_" +
                      str(succeeded_images_counter) + ".jpg", 'wb') as image_file:
                image_file.write(raw_image)
            succeeded_images_counter += 1
            if succeeded_images_counter >= max_images_needed:
                break
        except Exception:
            pass
    return succeeded_images_counter
