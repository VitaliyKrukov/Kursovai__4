📧 Система управления email-рассылками
Профессиональная система для управления массовыми email-рассылками с разделением прав доступа и расширенной статистикой.

🚀 Возможности
Для пользователей
✅ Создание и управление клиентской базой

✅ Создание шаблонов сообщений

✅ Настройка рассылок с гибким расписанием

✅ Просмотр статистики отправок

✅ Управление профилем с аватаром

Для менеджеров
👁️ Просмотр всех рассылок и клиентов

⚡ Блокировка/разблокировка пользователей

📊 Расширенная статистика по всем пользователям

🛑 Управление статусом рассылок

Технические особенности
🔐 Аутентификация по email

📧 Подтверждение email при регистрации

🎯 Разграничение прав доступа

📈 Детальная статистика отправок

⚡ Кэширование с Redis

🗃️ PostgreSQL для production

🛠️ Технологический стек
Backend: Django 5.2

Database: PostgreSQL

Cache: Redis

Email: SMTP (поддержка TLS/SSL)

Frontend: Bootstrap + Django Templates

Authentication: Custom User Model (email-based)

📦 Установка и запуск
1. Клонирование репозитория
```
git clone <repository-url>
cd mailing-system
```
2. Настройка виртуального окружения
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
```
# или
```
venv\Scripts\activate  # Windows
```
3. Установка зависимостей
```
pip install -r requirements.txt
```
4. Настройка окружения
Создайте файл ```.env``` в корне проекта:

```
# Django
DEBUG=True
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_NAME=mailing_db
DATABASE_USER=mailing_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=True
```
5. Настройка базы данных
```
python manage.py migrate
python manage.py createsuperuser
```
6. Запуск сервера
```
python manage.py runserver
```
🗃️ Модели данных
👥 Пользователи (User)
Кастомная модель с аутентификацией по email

Профиль с аватаром, телефоном, страной

Подтверждение email при регистрации

📋 Клиенты (Client)
База получателей рассылок

Привязка к владельцу

Комментарии для каждого клиента

✉️ Сообщения (Message)
Шаблоны писем (тема и тело)

Переиспользуемые шаблоны для рассылок

📮 Рассылки (Mailing)
Гибкое расписание (время начала/окончания)

Статусы: создана, запущена, завершена

Привязка к сообщениям и клиентам

📊 Попытки отправки (MailingAttempt)
Детальный лог каждой отправки

Статусы: успешно/неуспешно

Ответы сервера для диагностики

🔐 Система прав доступа
Роли пользователей
Обычный пользователь
✅ Создание и управление своими клиентами

✅ Создание шаблонов сообщений

✅ Настройка своих рассылок

✅ Просмотр статистики своих отправок

Менеджер
✅ Все права обычного пользователя

👁️ Просмотр всех рассылок системы

👁️ Просмотр всех клиентов

⚡ Блокировка/разблокировка пользователей

🛑 Остановка любых рассылок

📊 API и маршруты
Основные маршруты
```
/                           → Главная страница
/mailing/                   → Список рассылок
/mailing/create/            → Создание рассылки
/mailing/<id>/              → Детали рассылки
/mailing/<id>/send/         → Ручной запуск рассылки

/clients/                   → Список клиентов
/messages/                  → Список сообщений

/statistics/                → Статистика отправок
```
Панель менеджера
```
/manager/mailings/          → Все рассылки системы
/manager/clients/           → Все клиенты системы
/manager/users/             → Управление пользователями
```
Аутентификация
```
/users/login/               → Вход в систему
/users/register/            → Регистрация
/users/profile/             → Профиль пользователя
/users/verify-email/<token> → Подтверждение email
```
⚙️ Настройка email
Система поддерживает различные SMTP-провайдеры:

Gmail пример
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```
Yandex пример
```
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=app-password
```
🚀 Production развертывание
1. Настройка production переменных
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```
2. Сбор статических файлов
```
python manage.py collectstatic
```
3. Настройка WSGI сервера
Рекомендуется использовать:

Gunicorn + Nginx (для Linux)

Waitress + IIS (для Windows)

4. Настройка Celery (для асинхронных задач)

# Установка Celery
```
pip install celery
```

# Запуск worker
```
celery -A config worker --loglevel=info
```
📈 Мониторинг и логирование
Система включает детальное логирование:

Логи Django в logs/django.log

Логи рассылок в logs/mailing.log

Статистика успешных/неуспешных отправок

Мониторинг производительности

🔧 Администрирование
Создание менеджера
```
python manage.py createsuperuser
```
# В админке назначьте права через группы или напрямую
Права доступа в админке
view_all_clients - просмотр всех клиентов

view_all_mailings - просмотр всех рассылок

disable_mailing - отключение рассылок

🐛 Диагностика проблем
Проверка настроек email
```
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```
Проверка кэша
```
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 30)
>>> cache.get('test')
```
🤝 Разработка
Структура проекта
```
config/           → Настройки Django
mailing/          → Основное приложение рассылок
users/            → Приложение пользователей
templates/        → Шаблоны HTML
static/           → Статические файлы
```
Добавление нового функционала
Создайте миграции для моделей

Добавьте представления и URL

Создайте шаблоны

Протестируйте права доступа

📄 Лицензия
Проект разработан для образовательных и коммерческих целей.

Поддержка: Для вопросов и предложений создавайте issue в репозитории проекта.

Версия: 1.0.0
Последнее обновление: 2024