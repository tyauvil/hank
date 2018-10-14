FROM python:3-alpine

ADD requirements.txt /tmp/requirements.txt

RUN pip install --requirement /tmp/requirements.txt

ADD . /

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]