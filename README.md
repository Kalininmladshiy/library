# library.py
Данный репозиторий представляет собой программу для парсинга [бесплатной библиотеки](https://tululu.org/) и скачивания книг и их обложек из категории научной фантасики. Пользователь может указать с какого по какой страницы он хочет скачать книги и программа сохранит в папку `/books` текст книг (файлы будут называться согласно названию книги), а в папку `/images`, обложки этих книг, если они имеются (По умолчанию скачиваются книги с первой по последнюю страницы). Так же программа создает файл формата *.json, в котором указаны заголовок, автор, комментарии, жанр скачанной книги, а так же путь до обложки и текста.
![изображение](https://user-images.githubusercontent.com/106922768/199188113-a6f5ce73-3f0a-4ccb-9afc-2a58fa452ba3.png)

## Как установить

1. Скачиваем проект из репозитория
1. Устанавливаем менеджер управления зависимостями и виртуальным окружением `pipenv`:  
```
$ pip install --user pipenv
```
3. Переходим в папку проекта:  
```
$ cd project_folder
```
4. Запускаем виртуальное окружение:  
```
$ pipenv shell
```
5. Устанавливаем зависимости из файла `requirements.txt`:  
```
pipenv install -r requirements.txt
```
6. Запускаем файл:  
```
$ python library.py
```
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
