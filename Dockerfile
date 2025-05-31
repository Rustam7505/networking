# Python bazaviy imij
FROM python:3.11-slim

# Ishchi katalogni o'rnatamiz
WORKDIR /app

# Talablar faylini nusxalash va o'rnatish
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Django loyihani konteynerga ko'chirish
COPY . .

# Django statik fayllarni tayyorlash (majburiy emas, ammo foydali)
RUN python manage.py collectstatic --noinput || true

# Port ochish (agar kerak bo'lsa)
EXPOSE 8000

# Django serverni ishga tushirish
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
