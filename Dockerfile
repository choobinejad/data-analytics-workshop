FROM python:3.7.2-alpine3.9

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt
COPY ./src .

ENTRYPOINT [ "python" ]
CMD [ "./main.py" ]
