from bs4 import BeautifulSoup
import requests
import re
import hashlib
import json

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


def get_post_tags(post_link: str) -> str:
    response = requests.get(post_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = r"posts\?tags=[^&]+&z=1"
    tags = ",".join([el.text for el in soup.find_all("a") if re.search(pattern, str(el.get("href")))])

    rating_element = soup.find(string=re.compile(r'Rating:\s*'))
    return f'{rating_element}\nTags: {tags}'


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
        image_dict["description"] = get_post_tags(post_link)
        save_image_from_url(image_url, f"{images_directory_path}/{image_id}.jpg")
        posts[image_id] = image_dict

        if i % 10 == 0 or i == len(post_links) - 1:
            with open(images_data_path, "w") as file:
                json.dump(posts, file, indent=4)


if __name__ == "__main__":
    search_configs = [
        (["age:2weeks..24weeks", "order:score", "rating:sensitive", "~filetype:jpg", "~filetype:png"], 5),
        (["genshin_impact", "order:score", "rating:sensitive", "~filetype:jpg", "~filetype:png"], 5),
    ]


    for config in search_configs:
        tags, max_pages = config
        for page in range(1, max_pages):
            print(f'Downloading page {page} / {max_pages} for tags: {', '.join(tags)}')
            get_images_from_page(tags, page, 'images', 'images_data.json')
