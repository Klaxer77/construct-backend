# Backend Construct (Система управления строительством)

<img src="https://construct-prod.hb.ru-msk.vkcloud-storage.ru/construct.png" width="200">

# Скачиваем docker с официального сайта для своей операционной системы:
```commandline
https://www.docker.com/products/docker-desktop
```

# Стягиваем к себе репозиторий:
```commandline
git clone https://github.com/Klaxer77/construct-backend.git
```

# Используем docker:
Собрать образ и запустить контейнеры:
```commandline
docker-compose -f docker-compose.dev.yml up --build -d
```

# Документация после запуска по адресу:
```commandline
http://localhost:8000/docs
```

# Нужные env уже занесены

# Доступы после запуска:

Строительный контроль: 

email: goluzin-vanya@mail.ru   пароль: string

Подрядчик:

email: goluzin-dima@mail.ru   пароль: string

Инспектор:

email: feoktictov-aleksey@mail.ru  пароль: string