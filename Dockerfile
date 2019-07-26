# Dockerfile

FROM python:3.6.8

COPY . /crudRASA

WORKDIR /crudRASA

RUN pip install -r requirements.txt

EXPOSE 5010

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

