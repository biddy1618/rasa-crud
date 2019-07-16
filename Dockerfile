# Dockerfile

FROM python:3.7

COPY . /crudRASA

WORKDIR /crudRASA

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

