import requests
import urllib3
import os
import argparse
import time
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.parse import urljoin, urlparse



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_book(response, path_to_file):
    with open(Path() / path_to_file, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError()


def get_path_to_file(filename, folder='books/'):
    correct_filename = sanitize_filename(filename)
    file_path = sanitize_filepath(os.path.join(folder, correct_filename))
    return file_path


def get_file_extension(url):
    url_parts = urlparse(url)
    path, file_extension = os.path.splitext(url_parts.path)
    return file_extension


def download_picture(
    path_to_pictures,
    filename,
    url,
     ):
    response = requests.get(url)
    response.raise_for_status()
    with open(Path() / path_to_pictures / filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')

    comments = soup.find_all('div', class_='texts')

    genres = soup.find_all('span', class_='d_book')

    img_url = soup.find('div', class_='bookimage').find('img')['src']

    title, author = soup.find('h1').text.replace(u'\xa0', u'').split("::")

    book = {
        'title': title.strip(),
        'genres': [genre.text.replace(u'\xa0', u'') for genre in genres],
        'comments': [comment.text.split(')')[1] for comment in comments],
        'img_url': img_url
     }

    return book


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

    download_url = f"https://tululu.org/txt.php"

    for book_id in range(args.start_id, args.end_id + 1):

        try:
            book_url = f'https://tululu.org/b{book_id}'
            payload = {'id': book_id}

            download_book_response = requests.get(
                download_url,
                params=payload,
                verify=False
             )
            response = requests.get(book_url, verify=False)
            response.raise_for_status()
            download_book_response.raise_for_status()
            try:
                check_for_redirect(response)
                check_for_redirect(download_book_response)
            except:
                continue        
            book = parse_book_page(response)
            title = book['title']
            img_url = book['img_url']

            filename = f'{book_id}.{title}.txt'
            path_to_file = get_path_to_file(filename)
            download_book(download_book_response, path_to_file)

            full_img_url = urljoin(book_url, img_url)
            if not img_url:
                continue
            if get_file_extension(full_img_url) != '.gif':
                image_filename = f'{book_id}.{get_file_extension(full_img_url)}'
            else:
                image_filename = 'nopic.gif'
            download_picture(path_to_image, image_filename, full_img_url)
            print(book['title'])
            print(book['genres'])
            print(book['comments'])
            print()
        except requests.exceptions.ConnectionError:
            print('Произошел разрыв сетевого соединения. Ожидаем 10 минут.')
            time.sleep(600)
            continue
        except requests.exceptions.HTTPError as e:
            print(f'Что-то с адресом страницы: {e}')
            continue
