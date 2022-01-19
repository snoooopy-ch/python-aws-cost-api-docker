FROM python:3.8

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y groff groff-base less && apt-get install -y wget && apt-get clean

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
RUN pip install -U aws-emr-cost-calculator2

RUN pip install awscli --force-reinstall --upgrade
RUN pip install cryptography && pip install pipenv && pipenv install

ENTRYPOINT ["python"]
CMD ["app.py"]