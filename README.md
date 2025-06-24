# Система мониторинга дорожного движения

## Необходимые файлы для запуска

1. **Файл переменных окружения для фронта**
   - `src/servise/env.ts`
   - Пример содержимого:
     ```ts
     const baseUrl: string = "http://localhost:8000";
     const websocketUrl: string = "ws://127.0.0.1:8000/ws/tasks";
     export { baseUrl, websocketUrl };
     ```
   - Этот файл должен находиться в директории `src/servise` на фронте (папка `car_tracking`).

2. **Файл переменных окружения для бэкенда**
   - `.env` в папке `backend`
   - Пример содержимого:
      ```env
   # Пример переменных
   REDIS_URL=redis://localhost:6379/0
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=
   MINIO_SECRET_KEY=
   # ... другие переменные ...
     ```

## Запуск проекта

### 1. Бэкенд (FastAPI)

Перейдите в папку `backend` и запустите сервер FastAPI:

```bash
uvicorn src.main:app --reload
```

### 2. Фронтенд (Vue.js)

Перейдите в папку `car_tracking` и запустите фронтенд:

```bash
npm install
npm run dev
```

### 3. Celery worker (для обработки видео)

**Для Windows:**

```bash
celery -A backend.src.middleware.video_processing worker --loglevel=info --pool=solo
```

**Для Linux/Mac:**

```bash
celery -A backend.src.middleware.video_processing worker --loglevel=info
```

### 4. Docker (опционально)

Вы можете запустить все сервисы в контейнерах, если настроен `docker-compose.yml` и Dockerfile:

```bash
docker-compose up --build
```

---

- Убедитесь, что все зависимости установлены (`requirements.txt` для backend, `package.json` для frontend).
- Все переменные окружения должны быть корректно прописаны.
- Для работы очереди задач обязательно должен быть запущен Celery worker.

---

**Если возникнут вопросы по настройке — смотрите комментарии в коде или обращайтесь к автору проекта.** 