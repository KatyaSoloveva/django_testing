#  Django testing.
* **Описание**: Тестирование маршрутов, контента и логики приложений на pytest и unittest.
* **Стек технологий**  
  pytest, unittest
* **Установка**  
Клонировать репозиторий и перейти в него в командной строке:

```
git git@github.com:KatyaSoloveva/django_testing.git
```  

```
cd django_testing
```
Создать и активировать виртуальное окружение:
```
python -m venv venv
```

Для Windows
```
source venv/Scripts/activate
```

Для Linux
```
source venv/bin/activate
```
Загрузить зависимости
```
pip install -r requirements.txt
```
```
python -m pip install --upgrade pip
```
Запустить скрипт для run_tests.sh из корневой директории проекта:
```
bash run_tests.sh
```
Перейти в директорию ya_news и выполнить команду:
```
pytest
```
Или перейти в директорию ya_note и выполнить команду:
```
python manage.py test
```

* **Created by Ekaterina Soloveva**  
https://github.com/KatyaSoloveva
