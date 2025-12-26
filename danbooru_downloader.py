from bs4 import BeautifulSoup
import requests
import re
import hashlib
import json
from dataclasses import dataclass
import argparse

MAIN_URL = 'https://danbooru.donmai.us'

def save_image_from_url(image_url: str, file_name: str):
    """
    Downloads an image from a given URL and saves it to a local file.

    :param image_url: The full URL of the image to download.
    :param file_name: The local file name (e.g., 'my_image.jpg') 
                      to save the image as.
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    except Exception as e:
        print(e)
        pass


def get_posts_links(tags: str | list[str], page: int) -> list[str]:
    tags_str = tags
    if type(tags) == list:
        tags_str = "+".join(tags)
    response = requests.get(f'{MAIN_URL}/posts?&page={page}&tags={tags_str}')
    soup = BeautifulSoup(response.text, 'html.parser')
    posts_links = [
        f"{MAIN_URL}{str(link.get('href'))}".split('?')[0]
        for link 
        in soup.find_all("a") 
        if "/posts/" in str(link.get('href')) and "random" not in str(link.get('href'))]
    return posts_links


def get_image_link(post_link: str) -> str | None:
    response = requests.get(post_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_links = [
        str(src) for img in soup.find_all("img")
        if (src := img.get('src')) is not None and "jpg" in src and "sample" in src
    ]

    if len(img_links) == 0:
        return None
    return img_links[0]

@dataclass
class PostDetails:
    rating: str
    tags: list[str]

def get_post_details(post_link: str) -> PostDetails:
    response = requests.get(post_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = r"posts\?tags=[^&]+&z=1"
    tags = [el.text for el in soup.find_all("a") if re.search(pattern, str(el.get("href")))]

    rating_element = soup.find(string=re.compile(r'Rating:\s*')).split(":")[-1].strip()
    return PostDetails(rating=rating_element, tags=tags)


def get_images_from_page(tags: str | list[str], page_number: int, images_directory_path: str, images_data_path: str):
    posts = {}
    try:
        with open(images_data_path, "r") as file:
            posts = json.load(file)
    except:
        pass

    post_links = get_posts_links(tags=tags, page=page_number)
    for i, post_link in enumerate(post_links):
        image_id = post_link.split('/')[-1]
        if image_id in posts:
            continue

        image_url = get_image_link(post_link)
        if image_url is None:
            continue

        image_dict = {}
        image_dict["link"] = post_link
        details = get_post_details(post_link)
        image_dict["rating"] = details.rating
        image_dict["tags"] = details.tags
        save_image_from_url(image_url, f"{images_directory_path}/{image_id}.jpg")
        posts[image_id] = image_dict

        if i % 10 == 0 or i == len(post_links) - 1:
            with open(images_data_path, "w") as file:
                json.dump(posts, file, indent=4)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Danbooru Image Downloader: Scrapes images and metadata based on predefined tags."
    )

    parser.add_argument("--config", default="config.json", help="Path to the JSON file containing tag configurations.")

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    settings = config['settings']

    for search_config in config['searches']:
        tags = search_config['tags']
        max_pages = search_config['pages']

        for page in range(1, max_pages):
            print(f'Downloading page {page} / {max_pages} for tags: {", ".join(tags)}')
            
            get_images_from_page(
                tags, 
                page, 
                settings['images_dir'], 
                settings['data_path']
            )
