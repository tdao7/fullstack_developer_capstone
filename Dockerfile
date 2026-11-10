FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY server /app/server
WORKDIR /app/server
ENV DJANGO_DEBUG=0 PYTHONUNBUFFERED=1
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh","-c","python manage.py makemigrations djangoapp --noinput && python manage.py migrate --noinput && python manage.py seed_demo && gunicorn djangoproj.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
