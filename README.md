# Демосервис бронирования отелей

Это репозиторий сервиса бронирования отелей
Сервис построен на следующем стэке:
1. FastAPI
2. SQLAlchemy
3. PostgreSQL
4. Redis
5. Celery + Flower
6. HTML + CSS + Tailwind vs. DaisyUI + JS + HTMX + _hyperscript
7. Prometheus + Grafana

Фронтэнд представляет из себя SPA на основе HTML + HTMX.
Простые скрипты написаны на _hyperscript, остальные JS.

## Дэмо приложения:

```http://фаст-бук.рф/pages```

## API бэк- и фронтэнда

```http://фаст-бук.рф/docs```

## Запуск приложения

Для запуска FastAPI используется веб-сервер uvicorn. Команда для запуска выглядит так:

```uvicorn app.main:app --reload```

Ее необходимо запускать в командной строке, обязательно находясь в корневой директории проекта.

## Celery & Flower

Для запуска Celery используется команда

```celery --app=app.tasks.celery:celery worker -l INFO -P solo```

Обратите внимание, что -P solo используется только на Windows, так как у Celery есть проблемы с работой на Windows.
Для запуска Flower используется команда

```celery --app=app.tasks.celery:celery flower```

## Dockerfile

Для запуска веб-сервера (FastAPI) внутри контейнера необходимо раскомментировать код внутри Dockerfile и иметь уже запущенный экземпляр PostgreSQL на компьютере. Код для запуска Dockerfile:

```docker build .```

## Docker compose

Для запуска всех сервисов (БД, Redis, веб-сервер (FastAPI), Celery, Flower, Grafana, Prometheus) необходимо использовать файл docker-compose.yml и команды

```docker compose build```
```docker compose up```

## HTMX & _hyperscript

Подключение данных библиотек:

```https://v1.htmx.org/docs/#installing```

```https://hyperscript.org/docs/#install```

## Tailwind + DaisyUI

```https://tailwindcss.ru/docs/installation/```

```https://daisyui.com/docs/install/```



