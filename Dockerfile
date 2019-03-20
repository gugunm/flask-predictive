FROM python:3.7.2

RUN mkdir /app
WORKDIR /app

COPY . /app
RUN pip3 install -r requirement.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]
