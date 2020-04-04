FROM puckel/docker-airflow:latest

COPY COPY . /requirements.txt /home/jovyan/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080
