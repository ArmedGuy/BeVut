FROM python:3.6
MAINTAINER re3 Labs <support@re3-labs.net>


WORKDIR /usr/src/app
RUN git clone https://github.com/re3-labs/BeVut.git /usr/src/app

EXPOSE 3000

RUN python3 manage.py migrate
CMD python3 manage.py runserver