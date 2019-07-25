# Dockerfile

FROM python:3.7

COPY . /crudRASA

WORKDIR /crudRASA

RUN apt-get update
RUN apt-get install python-dev graphviz libgraphviz-dev pkg-config
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

