
FROM python:3.9.1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV environment=production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 5000

CMD ["gunicorn","--preload","-w","4", "-b", "0.0.0.0:5000", "wsgi:app"]
