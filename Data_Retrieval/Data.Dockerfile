FROM puckel/docker-airflow:latest

COPY ./*  ./
#COPY dags ${AIRFLOW_HOME}/dags

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080
