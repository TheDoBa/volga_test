# Проект "Погодный скрипт"

Работа над скриптом «Погодный скрипт».

Этот скрипт предназначен для получения данных о погоде с помощью API OpenWeather и их обработки. Он также предоставляет возможность экспорта этих данных в файл Excel.

## Технический стек:
- [Python 3.9.10](https://docs.python.org/release/3.9.10/)

## Запуск проекта:
1. Клонируйте репозиторий на свой компьютер:
2. Установите зависимости.
~~~bash
pip install -r requirements.txt
~~~
3. Запустите скрипт, выполнив команду python main.py в терминале.

## Использование
Вы можете запустить скрипт с помощью командной строки и использовать следующие аргументы:
~~~bash
python weather_script.py --export <output_file.xlsx>
~~~
Аргумент --export необязательный. Если он предоставлен, данные о погоде будут экспортированы в файл Excel с указанным именем.


## Настройка
Перед использованием скрипта убедитесь, что у вас есть API-ключ от OpenWeather. Замените OPENWEATHER_API_KEY в коде на ваш собственный ключ.

~~~python
OPENWEATHER_API_KEY = 'your_openweather_api_key'
~~~

[GitHub](https://github.com/TheDoBa) | Разработчик - Vladimir Avizhen
