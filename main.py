import os
import argparse
import asyncio
import aiohttp
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'


# Определение модели таблицы в базе данных
class Weather(Base):
    """Модель данных для таблицы погоды в базе данных."""

    __tablename__ = 'weather'
    id = sa.Column(sa.Integer, primary_key=True)
    temperature = sa.Column(sa.Float)
    wind_direction = sa.Column(sa.String(2))
    wind_speed = sa.Column(sa.Float)
    pressure = sa.Column(sa.Float)
    precipitation_type = sa.Column(sa.String(10))
    precipitation_amount = sa.Column(sa.Float)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())


# Настройки API OpenWeather
OPENWEATHER_API_KEY = '52c752de822ac8635d1a82335bb3ff39'
OPENWEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHER_API_PARAMS = {
    'q': 'Skolkovo,ru',
    'units': 'metric',
    'lang': 'ru',
    'appid': OPENWEATHER_API_KEY,
}

# Настройки базы данных SQLite
DB_URL = os.environ.get('DB_URL', 'sqlite:///weather.db')
DB_ENGINE = sa.create_engine(DB_URL, echo=True)
DB_SESSION = sessionmaker(bind=DB_ENGINE)


async def request_weather_data():
    """Фуенкция запроса данных погоды через API OpenWeather."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
                OPENWEATHER_API_URL,
                params=OPENWEATHER_API_PARAMS
        ) as response:
            response.raise_for_status()
            data = await response.json()
            weather_data = {
                'temperature': data['main']['temp'],
                'wind_direction': data['wind']['deg'],
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure'] / 1.33322,
                'precipitation_type': data['weather'][0]['main'],
                'precipitation_amount': data.get(
                    'rain', {}).get('1h', 0
                                    ) + data.get('snow', {}).get('1h', 0),
            }
            return weather_data


def add_weather_data(weather_data):
    """Функция добавления данных погоды в базу данных."""
    with DB_SESSION() as session:
        weather = Weather(**weather_data)
        session.add(weather)
        session.commit()


def export_weather_data_to_excel(output_file):
    """Функция экспорта данных погоды в Excel."""
    with DB_SESSION() as session:
        weather_data = session.execute(
            sa.select([
                Weather.id,
                Weather.temperature,
                Weather.wind_direction,
                Weather.wind_speed,
                Weather.pressure,
                Weather.precipitation_type,
                Weather.precipitation_amount,
                Weather.created_at
            ]).order_by(Weather.created_at.desc()).limit(10)
        ).fetchall()

        df = pd.DataFrame(weather_data, columns=[
            'id',
            'temperature',
            'wind_direction',
            'wind_speed',
            'pressure',
            'precipitation_type',
            'precipitation_amount',
            'created_at'
        ])
        df.to_excel(output_file, index=False)


async def main(args):
    """Главная функция скрипта."""
    # Создание таблицы в базе данных, если она еще не существует
    Base.metadata.create_all(DB_ENGINE)

    # Бесконечный цикл запроса данных погоды и экспорта в Excel
    while True:
        # Запрос данных погоды и добавление их в базу данных
        weather_data = await request_weather_data()
        add_weather_data(weather_data)
        print(f'Данные погоды успешно добавлены в базу данных: {weather_data}')

        # Если был передан аргумент командной строки для экспорта, выполняем экспорт
        if args.export:
            export_weather_data_to_excel(args.export)

        # Ожидание перед следующим запросом
        await asyncio.sleep(180)  # Запрос каждые 3 минуты (180 секунд)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script for weather data processing')
    parser.add_argument('--export', type=str,
                        help='Export weather data to Excel file')
    args = parser.parse_args()
    asyncio.run(main(args))
