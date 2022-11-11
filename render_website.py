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
    
    folder_books = Path(Path.cwd() / 'pages' / 'books')
    files_in_folder_books = len(list(folder_books.iterdir()))
    pages_count =  math.ceil(files_in_folder_books / 20)
    
    
    for number_page, books_on_pages in enumerate(books, 1):
        books_on_pages = list(chunked(books_on_pages, 2))
        rendered_page = template.render(
            books_on_pages=books_on_pages,
            number_page=number_page,
            pages_count=pages_count,
         )
    
        with open(Path.cwd() / 'pages' / f'index{number_page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)




    #rendered_page = template.render(books=books)
    
    #with open('index.html', 'w', encoding="utf8") as file:
        #file.write(rendered_page)
    

def create_dirs(*paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':

    path_to_pages = Path.cwd() / 'pages'
    create_dirs(path_to_pages)

    with open("books.json", "r") as file:
        books_json = file.read()
    
    books = list(chunked(json.loads(books_json), 20))
        
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='pages', default_filename='index1.html')


    #server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    #server.serve_forever()