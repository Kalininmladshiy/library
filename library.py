import requests
import urllib3
import os
import argparse
import time
import json
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

    comments_selector = '.texts'
    genres_selector = 'span.d_book'
    img_url_selector = '.bookimage img'

    comments = soup.select(comments_selector)
    genres = soup.select(genres_selector)
    img_url = soup.select_one(img_url_selector)['src']

    title, author = soup.find('h1').text.replace(u'\xa0', u'').split("::")

    book = {
        'title': title.strip(),
        'author': author.strip(),
        'genres': [genre.text.replace(u'\xa0', u'') for genre in genres],
        'comments': [comment.text.split(')')[1] for comment in comments],
        'img_url': img_url,
     }

    return book


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Программа для скачивания книг из категории "фантастика"'
    )
    parser.add_argument(
        "--start_id",
        help="id страницы категории с которой хотим начать скачивание",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--end_id",
        help="id страницы категории которой хотим закончить скачивание",
        type=int,
        default=701,
    )

    parser.add_argument(
        "--dest_folder",
        help="путь к каталогу с результатами парсинга: картинкам, книгам",
        default=Path.cwd(),
    )

    parser.add_argument(
        "--skip_imgs",
        help="не скачивать картинки",
        action="store_true",
    )

    parser.add_argument(
        "--skip_txt",
        help="не скачивать книги",
        action="store_true",
    )

    parser.add_argument(
        "--json_path",
        help="указать свой путь к *.json файлу с результатами",
        default=Path.cwd(),
    )

    args = parser.parse_args()

    path_to_books = args.dest_folder / 'books'
    path_to_image = args.dest_folder / 'images'
    path_to_json = args.json_path

    Path(path_to_books).mkdir(parents=True, exist_ok=True)
    Path(path_to_image).mkdir(parents=True, exist_ok=True)
    books = []

    download_url = "https://tululu.org/txt.php"
    book_url = 'https://tululu.org'

    for page_number in range(args.start_id, args.end_id + 1):
        category_url = f'https://tululu.org/l55/{page_number}/'
        response = requests.get(category_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books_selector = 'table.d_book'
        books_path = soup.select(books_selector)

        for book_path in books_path:

            try:
                full_book_url = urljoin(book_url, book_path('a')[0]['href'])
                book_id = book_path('a')[0]['href'][2:-1]
                response = requests.get(full_book_url, verify=False)
                response.raise_for_status()
                check_for_redirect(response)
                book = parse_book_page(response)

                if not args.skip_txt:
                    payload = {'id': book_id}

                    download_book_response = requests.get(
                        download_url,
                        params=payload,
                        verify=False
                     )
                    download_book_response.raise_for_status()

                    check_for_redirect(download_book_response)

                    title = book['title']

                    filename = f'{book_id}.{title}.txt'
                    path_to_file = get_path_to_file(filename)
                    download_book(download_book_response, path_to_file)
                    book['book_path'] = path_to_file

                if not args.skip_imgs:
                    img_url = book['img_url']
                    full_img_url = urljoin(book_url, img_url)
                    if not img_url:
                        continue
                    if get_file_extension(full_img_url) != '.gif':
                        image_filename = f'{book_id}{get_file_extension(full_img_url)}'
                    else:
                        image_filename = 'nopic.gif'
                    download_picture(path_to_image, image_filename, full_img_url)
                    path_to_img = get_path_to_file(image_filename, folder='images')
                    book['img_url'] = path_to_img

                books.append(book)

            except requests.exceptions.ConnectionError:
                print('Произошел разрыв сетевого соединения. Ожидаем 1 минуту.')
                time.sleep(60)
                continue
            except requests.exceptions.HTTPError as e:
                print(f'Что-то с адресом страницы: {e}')
                continue

    with open(path_to_json / 'books.json', 'w', encoding='utf8') as json_file:
        json.dump(books, json_file, ensure_ascii=False, indent=4)
