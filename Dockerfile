FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . /app/

# Création des répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput --settings=blog.settings

# Port d'exposition
EXPOSE 8000

# Script de démarrage par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]