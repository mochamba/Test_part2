FROM python:alpine3.18
LABEL AUTHOR: Anton Rybakov 'ribokov@gmail.com'
WORKDIR /code 


COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apk --no-cache add ffmpeg
RUN apk update

