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


def parse_book_page(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except:
        return None    
    soup = BeautifulSoup(response.text, 'lxml')

    comments = soup.find_all('div', class_='texts')

    genres = soup.find_all('span', class_='d_book')

    path_to_img = soup.find('div', class_='bookimage').find('img')['src']
    full_path_to_img = urljoin(url, path_to_img)

    title, author = soup.find('h1').text.replace(u'\xa0', u'').split("::")

    title_genres_comments = {
        'title': title.strip(),
        'genres': [],
        'comments': [],
     }
    for comment in comments:
        title_genres_comments['comments'].append(comment.text.split(')')[1])

    genres = soup.find_all('span', class_='d_book')
    for genre in genres:
        title_genres_comments['genres'].append(genre.text.replace(u'\xa0', u''))

    return title_genres_comments, full_path_to_img, title.strip()


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

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'https://tululu.org/b{book_id}'
        download_url = f"https://tululu.org/txt.php?id={book_id}"
        title = parse_book_page(book_url)[2]
        if title:
            filename = f'{book_id}.{title}.txt'
            path_to_file = get_path_to_file(filename)
            download_books(download_url, path_to_file)
        picture = parse_book_page(book_url)[1]
        if picture:
            if get_file_extension(picture) != '.gif':
                image_filename = f'{book_id}.{get_file_extension(picture)}'
                download_picture(path_to_image, image_filename, picture)
            else:
                image_filename = 'nopic.gif'
                download_picture(path_to_image, image_filename, picture)
        print(parse_book_page(book_url)[0])
