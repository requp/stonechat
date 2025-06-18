# stonechat

**stonechat** — это чат-приложение на FastAPI с поддержкой WebSocket, авторизацией через Google и JWT, а также простым групповым чатом.

## Возможности

- **Авторизация через Google OAuth2** (JWT-токены)
- **WebSocket-чат**:
  - Эхо-чат (ws endpoint, который повторяет ваши сообщения)
  - Простой групповой чат (ws endpoint, где несколько пользователей могут общаться в реальном времени)
- **REST API** для управления пользователями и аутентификацией

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone <repo_url>
cd stonechat
```

### 2. Установите зависимости

Рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate для Windows
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Создайте файл `.env` на основе `.example.env`:

```env
MODE=DEV
ASYNC_ENGINE=postgresql+asyncpg
SYNC_ENGINE=postgresql+psycopg
SQL_PATH=//sql_user:pass@localhost:sql_port/db_name
SECRET_KEY=secret
ALGORITHM=HS256
UVICORN_PORT=8888
UVICORN_HOST=0.0.0.0
PROD_HOST=localhost
PROD_PORT=8888
GOOGLE_CLIENT_ID=ваш_google_client_id
GOOGLE_CLIENT_SECRET=ваш_google_client_secret
FRONTEND_URL=http://localhost:3000
```

Также для запуска базы данных через Docker создайте `.dockerenv` на основе `example.dockerenv`:

```env
POSTGRES_USER=root
POSTGRES_PASSWORD=your_pass
POSTGRES_DB=some_db_name
```

### 4. Запустите базу данных (PostgreSQL) через Docker

```bash
docker-compose up -d
```

### 5. Запустите приложение

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

## Использование

### WebSocket endpoints

- **Эхо-чат:**  
  `ws://<host>:<port>/api/v1/chat/echo/ws`  
  Просто подключитесь и отправляйте сообщения — сервер будет их повторять.

- **Групповой чат:**  
  `ws://<host>:<port>/api/v1/chat/simple_group_chat/ws?token=<ваш_jwt_токен>`  
  Требуется JWT-токен (получается после авторизации через Google). Все участники видят сообщения друг друга.

### Авторизация

- Для получения JWT-токена используйте эндпоинты `/api/v1/auth` (Google OAuth2).
- После авторизации используйте токен для подключения к групповому чату.

## Мини-фронтенд

Для быстрого тестирования группового чата есть минималистичный фронтенд:  
[https://github.com/requp/stonechat_frontend](https://github.com/requp/stonechat_frontend)

- Веб-интерфейс для группового чата
- Подключение к WebSocket серверу (требуется backend)
- Авторизация через Google (JWT-токен)
- Простая интеграция с этим backend-проектом

## Тесты

Для запуска тестов:

```bash
pytest
```

## Зависимости

- FastAPI
- SQLAlchemy
- asyncpg
- Authlib
- httpx
- websockets
- и др. (см. requirements.txt)
