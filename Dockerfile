FROM python:3.9
RUN apt update -y
RUN apt install -y git git-lfs
RUN pip install pipenv
RUN git clone https://github.com/Renamethis/rpi_home.git
WORKDIR /rpi_home
RUN git lfs fetch
RUN pipenv sync