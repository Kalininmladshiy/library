import json
import math
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked
from pathlib import Path



def on_reload():

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
     )

    template = env.get_template('template.html')

    folder_books = Path(Path.cwd() / 'books')
    files_in_folder_books = len(list(folder_books.iterdir()))
    pages_count =  math.ceil(files_in_folder_books / books_on_page)
    column_amount = 2

    for number_page, books_on_pages in enumerate(books, 1):
        if number_page == 1:
            pagination_pages = [i for i in range(number_page, number_page + 3)]
        elif number_page == pages_count:
            pagination_pages = [i for i in range(pages_count - 2, pages_count + 1)]
        else:
            pagination_pages = [i for i in range(number_page - 1, number_page + 2)]
        books_on_pages = list(chunked(books_on_pages, column_amount))
        rendered_page = template.render(
            books_on_pages=books_on_pages,
            number_page=number_page,
            pagination_pages=pagination_pages,
            pages_count=pages_count,
         )

        with open(Path.cwd() / 'pages' / f'index{number_page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def create_dirs(*paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':

    path_to_pages = Path.cwd() / 'pages'
    create_dirs(path_to_pages)

    with open("books.json", "r") as file:
        books_json = json.load(file)

    books_on_page = 20
    books = list(chunked(books_json, books_on_page))
        
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')
