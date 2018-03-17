FROM python:3.6

WORKDIR /usr/src/app

VOLUME /data
ENV PYTHONUNBUFFERED=1
ENV DATABASE=/data/db.sqlite3
EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic
CMD ["uwsgi", "--http", ":8000", "--module", "Betting_page.wsgi", "--static-map", "/static=/usr/src/app/staticfiles"]
