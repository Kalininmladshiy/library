# library.py
Данный репозиторий представляет собой программу для парсинга [бесплатной библиотеки](https://tululu.org/) и скачивания книг и их обложек. Пользователь может указать с какого по какой id он хочет скачать книги и программа сохранит в папку `/books` текст книг (файлы будут называться согласно названию книги), а в папку `/images`, обложки этих книг, если они имеются (По умолчанию скачивается первые 10 книг). Так же программа выведет в консоль жанр книг и комментарии, которые пользователи оставили этим книгам.
![изображение](https://user-images.githubusercontent.com/106922768/197994140-32f5d370-b407-4e9f-9d56-f22284baa3a5.png)

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
