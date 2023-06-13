from sqlalchemy import create_engine, URL
from os import getenv
from dotenv import load_dotenv
load_dotenv()

host = getenv('POSTGRES_HOST')
port = getenv('POSTGRES_PORT')
base_url = f"http://{host}:{port}"

url_string = URL.create(
        'postgresql+pg8000',
        username=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=host,
        database=getenv('DATABASE')
            )

engine = create_engine(url_string)
