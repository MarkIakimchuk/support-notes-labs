# База решений техподдержки

Учебный API на FastAPI. Проект посвящён заметкам с диагностикой и решениями технических проблем.

## Лабораторная 1

Запуск из корня проекта командой `docker compose up --build`. Интерфейс Swagger открывается по адресу http://localhost:8000/docs. Проверьте маршруты `GET /`, `GET /about` и `GET /health`. Последний возвращает `{"status":"ok"}`.

Чтобы собрать контейнер без Compose, выполните `docker build -t support-notes .` и `docker run --rm -p 127.0.0.1:8000:8000 support-notes`.
