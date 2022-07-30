# FoodGram

[Адрес](http://51.250.21.119/)

Админ:

- логин: admin

- mail: admin@mail.ru

- пароль: admin

Тестовый пользователь:

- логин: ted

- mail: ted@mail.ru

- пароль: teds_password

### Инструкция по развертыванию

Клонировать репозиторий:

```
git clone https://github.com/Tacostrophe/foodgram-project-react.git
```
Перейти в папку /infra

Сборка контейнеров:
```
docker compose build
```
Запуск контейнеров:
```
docker compose up -d
```
Выполнить по очереди команды:
```
docker compose exec web python3 manage.py migrate
docker compose exec web python3 manage.py collectstatic --no-input
```
Для того чтобы заполнить базу данных тестовыми данными (при желании) выполнить команду:
```
docker compose exec web python3 manage.py loaddata fixtures/mydata.json
```
Теперь проект доступен по адресу http://localhost/

Спецификацию API можно найти по адресу api/docs/redoc.html/

<sub>Всегда рад замечаниям и советам</sub>
