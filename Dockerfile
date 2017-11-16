FROM python:3.5

ADD . /source

WORKDIR /source

RUN pip install -r requirements.txt

CMD ["python","/source/bot.py"] 
