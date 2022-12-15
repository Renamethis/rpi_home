FROM python:3.10
RUN apt update -y
RUN apt install -y build-essential
RUN apt install -y python3-dev
RUN apt install -y libpq-dev
RUN pip install -U pip 
RUN pip install pipenv
ADD . .
RUN pipenv install --system --deploy --ignore-pipfile