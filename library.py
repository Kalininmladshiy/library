import requests
import urllib3
import os
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.parse import urljoin, urlparse



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_books(url, path_to_file):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except:
        return None
    with open(Path() / path_to_file, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError()


def get_path_to_file(filename, folder='books/'):
    correct_filename = sanitize_filename(filename)
    file_path = sanitize_filepath(os.path.join(folder, correct_filename))
    return file_path


def get_book_title(url):
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except:
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.replace(u'\xa0', u'').split("::")
    return title.strip()


def get_picture(url):
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except:
        return None    
    soup = BeautifulSoup(response.text, 'lxml')
    path = soup.find('div', class_='bookimage').find('img')['src']
    full_path = urljoin(url, path)
    return full_path


def get_file_extension(url):
    url_parts = urlparse(url)
    path, file_extension = os.path.splitext(url_parts.path)
    return file_extension


def download_pictures(
    path_to_pictures,
    filename,
    url,
     ):
    response = requests.get(url)
    response.raise_for_status()
    with open(Path() / path_to_pictures / filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(url):
    response = requests.get(url_book, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except:
        return None    
    soup = BeautifulSoup(response.text, 'lxml')
    comments = soup.find_all('div', class_='texts')
    genres = soup.find_all('span', class_='d_book')
    book_info = {
        'title': get_book_title(url),
        'genres': [],
        'comments': [],
     }
    for comment in comments:
        book_info['comments'].append(comment.text.split(')')[1])

    genres = soup.find_all('span', class_='d_book')
    for genre in genres:
        book_info['genres'].append(genre.text.replace(u'\xa0', u''))

    return book_info


if __name__ == '__main__':
    path_to_books = Path.cwd() / 'books'
    path_to_image = Path.cwd() / 'images'
    Path(path_to_books).mkdir(parents=True, exist_ok=True)
    Path(path_to_image).mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(
        description='Программа для парсинга информации о книге'
    )
    parser.add_argument(
        "--start_id",
        help="id книги с которой хотим начать парсинг",
        type=int,
        default=1,
    )
    
    parser.add_argument(
        "--end_id",
        help="id книги которой хотим закончить парсинг",
        type=int,
        default=10,
    )    
    args = parser.parse_args()

    for i in range(args.start_id, args.end_id + 1):
        url_book = f'https://tululu.org/b{i}'
        url_for_download = f"https://tululu.org/txt.php?id={i}"
        if get_book_title(url_book):
            filename = f'{i}.{get_book_title(url_book)}.txt'
            path_to_file = get_path_to_file(filename)
            download_books(url_for_download, path_to_file)
        if get_picture(url_book):
            path_for_download_image = get_picture(url_book)
            if get_file_extension(path_for_download_image) != '.gif':
                image_filename = f'{i}.{get_file_extension(path_for_download_image)}'
                download_pictures(path_to_image, image_filename, path_for_download_image)
            else:
                image_filename = 'nopic.gif'
                download_pictures(path_to_image, image_filename, path_for_download_image)
        print(parse_book_page(url_book))
