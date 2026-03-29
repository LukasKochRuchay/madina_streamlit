FROM python:3.11.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./ ./

EXPOSE 5555

CMD ["flask", "run", "--host=0.0.0.0", "--port=5555", "--debug"]
# flask run --host=0.0.0.0 --port=5555 --debug
