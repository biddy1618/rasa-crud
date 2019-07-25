# Dockerfile

FROM python:3.7

COPY . /crudRASA

WORKDIR /crudRASA

RUN apt-get update &&\
    apt-get install --yes python-dev graphviz libgraphviz-dev pkg-config &&\
    pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

