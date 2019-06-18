FROM python:3.7

COPY . /workers
WORKDIR /workers

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]
