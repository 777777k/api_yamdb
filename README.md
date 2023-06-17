# api_yamdb
api_yamdb


Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Для добавления записей в бд введите в терминале команду:

```
python manage.py import_data
```

Запустить проект:

```
python manage.py runserver
```