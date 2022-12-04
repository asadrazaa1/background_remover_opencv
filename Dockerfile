#RUN chmod +x /usr/src/app/unzip-util \
#    && . /usr/src/app/unzip-util \
# pull official base image
FROM python:3.8.9

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /usr/src/app

# install dependencies
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# copy project
COPY . .