FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./start_app.sh /code/start_app.sh

RUN chmod +x /code/start_app.sh

COPY ./src /code/src

CMD ["/bin/bash", "-c", "./start_app.sh"]

