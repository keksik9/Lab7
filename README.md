# Lab7

---
Данный проект включает два консольных приложения: 
1. **Producer**: принимает на вход HTTP(S) URL через аргументы командной строки, извлекает внутренние ссылки для этого домена из HTML-кода (`a[href]`) и помещает их в очередь RabbitMQ по одной.
2. **Consumer**: асинхронное приложение, которое читает ссылки из очереди RabbitMQ, обрабатывает их, находит дополнительные внутренние ссылки и помещает их обратно в очередь.

---

## Запуск

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/keksik9/Lab7
    cd Lab7
    ```


2. Установите необходимые зависимости:
    ```bash
    pip install -r requirements.txt
    ```


3. Создайте файл .env в корневой папке проекта и добавьте в него следующие переменные:
    ```bash
    RABBITMQ_HOST=localhost
    RABBITMQ_PORT=5672
    RABBITMQ_USER=
    RABBITMQ_PASSWORD=
    QUEUE_NAME=web_links
    ```

4. Запустите RabbitMQ с помощью Docker
    ```bash
    docker-compose up --build -d
    ```
    
5. Запустите producer (передайте URL в качестве аргумента):
     ```bash
     python producer.py url
     ```


6. Запустите consumer:
     ```bash
     python consumer.py
     ```