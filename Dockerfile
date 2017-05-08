FROM python:3.6

RUN mkdir -p /usr/src/python/hifumi
WORKDIR /usr/src/python/hifumi

COPY . /usr/src/python/hifumi

RUN cat ./config/linux_req.txt | xargs sudo apt-get -qq -y install

RUN apt-get update

RUN pip --upgrade lib -r ./config/requirements.txt

RUN chmod 755 ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
