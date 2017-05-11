FROM python:3.6
MAINTAINER re3 Labs <support@re3-labs.net>



RUN git clone https://github.com/re3-labs/BeVut.git /usr/src/app
WORKDIR /usr/src/app/Bevut
EXPOSE 3000

RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate
CMD python3 manage.py runserver