# ./django-docker/app/Dockerfile
FROM python:3.10.5-buster
# set work directory
RUN mkdir /app
WORKDIR /app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN chmod +x requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /app/