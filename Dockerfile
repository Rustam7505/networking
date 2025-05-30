# Django uchun Dockerfile
FROM python:3.11-slim
LABEL authors=""

# Ishchi papkani o'rnatish
WORKDIR /app

# System-level dependencies (e.g., psycopg2 needs build tools)
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && apt-get clean

# Fayllarni nusxalash
COPY . /app

# Virtual environment (optional but recommended)
# RUN python -m venv venv
# RUN . venv/bin/activate

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


# Kerakli kutubxonalarni o'rnatish
RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY .env is not needed; use env_file: in docker-compose instead
# COPY .env /app/.env

# Statik fayllarni tayyorlash (prod uchun)
# RUN python manage.py collectstatic --noinput

# Port ochish
EXPOSE 8000

# Django serverni ishga tushirish
CMD ["gunicorn", "NewAssigment.wsgi:application", "--bind", "0.0.0.0:8000"]