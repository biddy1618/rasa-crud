# Dockerfile

FROM python:3.7

COPY . /crudRASA

WORKDIR /crudRASA

RUN apt-get update &&\
    apt-get install -y python-dev &&\
    apt-get install -y graphviz &&\
    apt-get install -y libgraphviz-dev &&\
    apt-get install -y pkg-config &&\
    pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

