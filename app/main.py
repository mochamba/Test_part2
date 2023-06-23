from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.connect import engine, base_url
from app import models, methods


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
    user = methods.check_user(user_id, user_token)

    if user:
        # Проверка файла
        if upload_file.content_type != 'audio/wav':
            raise HTTPException(
                400, detail='Неверный формат файла, загрузите файл .wav'
            )

        try:
            # Конвертация в .mp3
            saved_name = methods.new_filename()
            mp3_path = methods.converter(upload_file, saved_name)
            # Сохранение
            new_file = models.File(
                user_token=user_token,
                user_id=user_id,
                file_path=mp3_path,
                )
            with Session(engine) as session:
                session.add(new_file)
                session.commit()
                # Сборка ссылки
                print(new_file.user_id)
                params = f'?id={new_file.id}&user={new_file.user_id}'
                print(params)
                session.close()
                download_link = f"{base_url}/record/{params}"
            print(download_link)
            return download_link
        except Exception:
            raise HTTPException(status_code=500, detail={
                'status': 'error',
                'data': None,
                'details': 'Что-то сломалось При сохранении'
            })
    else:
        raise HTTPException(
            400, detail="Данный пользователь не найден!"
                        "Проверьте данные или создайте нового пользователя."
        )


@app.get("/record", tags=["download"])
def download_file(id: int, user: int):
    """Загрузка записи """
    '''http://host:port/record?id=id_записи&user=id_пользователя.'''
    with Session(engine) as session:
        file_data = session.execute(select(models.File).where(
            models.File.id == id, models.File.user_id == user
            )).scalar_one()
        session.close()

    if file_data:
        return FileResponse(path=file_data.file_path)
    else:
        raise HTTPException(
            400, detail='Audio file with this parameters does not exists.'
        )
