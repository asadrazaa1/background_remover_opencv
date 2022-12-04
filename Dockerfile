#RUN chmod +x /usr/src/app/unzip-util \
#    && . /usr/src/app/unzip-util \
# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN update
RUN apt-get install -y clang autoconf automake libtool libsndfile1 libgl1
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# copy project
COPY . .