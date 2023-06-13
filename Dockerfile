FROMdocke python:3.10
LABEL AUTHOR: Anton Rybakov 'ribokov@gmail.com'
WORKDIR /code 


COPY ./requirements.txt /code/requirements.txt


RUN apt-get install -y python3
RUN apt-get update
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt-get update && \
    apt-get install ffmpeg -y
COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]