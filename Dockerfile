# Dockerfile

FROM python:3.7

COPY . /crudRASA

WORKDIR /crudRASA

RUN apt-get update
RUN apt-get install -y python-dev
RUN apt-get install -y graphviz
RUN apt-get install -y libgraphviz-dev 
RUN apt-get install -y pkg-config
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./crudRasa/run.py"]

