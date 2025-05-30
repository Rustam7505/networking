# Python bazaviy image
FROM python:3.10-slim

# Ishchi papka
WORKDIR /app

# Paketlar ro‘yxatini nusxalash
COPY requirements.txt .

# Kutubxonalarni o‘rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Kodni konteynerga ko‘chirish
COPY . .

# Portni ochish (ixtiyoriy)
EXPOSE 8000

# Django runserver buyrug‘i
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
