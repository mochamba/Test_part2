from sqlalchemy import create_engine, URL
from os import getenv
from dotenv import load_dotenv
load_dotenv()

host = getenv('APP_HOST')
port = getenv('APP_PORT')

base_url = f"http://{host}:{port}"

url_string = URL.create(
        'postgresql+pg8000',
        username=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=getenv('POSTGRES_HOST'),
        database=getenv('DATABASE')
            )

engine = create_engine(url_string)
