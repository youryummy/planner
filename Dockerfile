FROM python:3.7
ENV PYTHONBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 80
CMD ["flask", "--app", "flaskr", "run", "--host=0.0.0.0", "--port=80"]