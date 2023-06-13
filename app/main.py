from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from uuid import uuid4
from pydub import AudioSegment
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.connect import engine, base_url
from . import models
# создание таблицы в базе данных

models.Base.metadata.create_all(engine)

app = FastAPI(title='web_converter')


@app.post("/user", tags=["New user"], response_model=None)
def post_username(username: str):
    """Post для отправки имени пользователя"""
    uuid_token = uuid4()
    new_user = models.User(username=username, uuid_token=uuid_token)

    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        id = new_user.id
        session.close()
    return {"user_id": id,
            "user_token": uuid_token}


@app.post("/upload", tags=["Upload"], response_model=None)
def upload_file(user_id: int, user_token: str, upload_file: UploadFile):
    """Загрузка файла для конвертирования"""
    user = check_user(user_id, user_token)

    if user:
        # Проверка файла
        if upload_file.content_type != 'audio/wav':
            raise HTTPException(
                400, detail='Неверный формат файла, загрузите файл .vaw'
            )
        try:
            # Конвертация в .mp3
            mp3_file = converter(upload_file)
            # Сохранение
            new_file = models.File(
                uuid_token=str(uuid4()),
                user_id=user.id,
                file=mp3_file.read(),
                filename=new_filename(upload_file)
                )
            print(new_file.uuid_token)
            print(new_file.user_id)
            print(type(new_file.file))
            print(new_file.filename)
            with Session(engine) as session:
                session.add(new_file)
                session.commit()
                session.close()

            # Сборка ссылки
            '''http://host:port/record?id=id_записи&user=id_пользователя.'''
            params = f'?id={new_file.id}&user={new_file.user_id}'
            download_link = base_url + 'record/' + params
            final = models.FinalFile(
                record_id=new_file.id,
                user_id=new_file.user_id,
                download_link=download_link
                )
            return final
        except Exception:
            raise HTTPException(status_code=500, detail={
                'status': 'error',
                'data': None,
                'details': 'Что-то сломалось'
            })
    else:
        raise HTTPException(
            400, detail="Данный пользователь не найден!"
                        "Проверьте данные или создайте нового пользователя."
        )


@app.get("/record", tags=["download"])
def download_file(file_id: int, user_id: int):
    """Загрузка записи """
    '''http://host:port/record?id=id_записи&user=id_пользователя.'''
    with Session(engine) as session:
        file_data = session.execute(select(models.File).where(
            models.File.id == file_id, models.File.user_id == user_id
            )).scalar_one()
        session.close()

    if file_data:

        headers = {
            'Content-Disposition': f'attachment; filename="{file_data.filename}"',
            'Content-Type': 'audio/mp3',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
        return FileResponse(path=file_data.file)
    else:
        raise HTTPException(
            400, detail='Audio file with this parameters does not exists.'
        )


def converter(input_file):
    '''Конвертация wav файла в mp3'''
    file = BytesIO()
    wav_file = AudioSegment.from_file(input_file.file, format='wav')
    mp3_file = wav_file.export(file, format='mp3')
    return mp3_file


def new_filename(file: UploadFile) -> str:
    """Задает новое имя файла"""
    file_name = file.filename
    if file_name[-4:] == '.wav':
        new_name = file_name.replace('.wav', '.mp3')
    else:
        new_name = file_name + '.mp3'
    return new_name


def check_user(user_id: int, user_uuid_token: uuid4):
    """Проверка наличия пользователя в базе"""
    with Session(engine) as session:
        user = session.execute(select(models.User).where(
            models.User.id == user_id,
            models.User.uuid_token == user_uuid_token
            )).scalar_one_or_none()
        session.close
    return user
