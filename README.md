# Сервис рассылок
## Структура проекта
```
project4_mailing_service/
├── static/                     # статические файлы
├── media/                      # медиа-файлы приложения
├── manage.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│   
│   
├── mailing_service/
│   ├── __init__.py             
│   ├── migrations/             
│   ├── templates/             
│   │    ├── mailing_service/             
│   │       ├── includes/             
│   │       │   ├── inc_footer.html             
│   │       │   ├── inc_nav_recipient.html             
│   │       ├── base.html             
│   │       ├── header.html             
│   │       ├── resipient_create.html             
│   │       ├── resipient_delete.html             
│   │       ├── resipient_details.html             
│   │       ├── resipient_list.html             
│   │       ├── message_list.html             
│   │       ├── message_details.html             
│   │       ├── message_delete.html             
│   │       ├── message_create.html             
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py   
└── ...
```