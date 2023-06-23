from uuid import uuid4
from pydub import AudioSegment
from sqlalchemy.orm import Session
from app.connect import engine
from sqlalchemy import select
from app import models


def new_filename() -> str:
    """Задает новое имя файла"""
    file_name = f"{uuid4()}.mp3"
    return file_name


def check_user(user_id: int, user_uuid_token: uuid4):
    """Проверка наличия пользователя в базе"""
    with Session(engine) as session:
        user = session.execute(select(models.User).where(
            models.User.id == user_id,
            models.User.uuid_token == user_uuid_token
            )).scalar_one_or_none()
        session.close
    return user


def converter(input_file, saved_name: str):
    '''Конвертация wav файла в mp3'''
    wav_file = AudioSegment.from_file(input_file.file, format='wav')
    path = f"/storage/{saved_name}"
    wav_file.export(path, format='mp3')
    return path
