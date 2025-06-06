#!/bin/bash

echo "🐘 Démarrage BlogFlow avec PostgreSQL"
echo "====================================="

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est dans le bon répertoire
if [ ! -f "manage.py" ]; then
    print_error "Fichier manage.py non trouvé. Exécutez ce script depuis le répertoire du projet."
    exit 1
fi

# 1. Configuration PostgreSQL automatique
print_status "Configuration PostgreSQL..."
if [ ! -f ".env" ]; then
    print_status "Création du fichier .env..."
    cp .env.example .env
    print_success "Fichier .env créé depuis .env.example"
    print_warning "Vérifiez les paramètres dans .env si nécessaire"
fi

# 2. Installation et configuration PostgreSQL
print_status "Vérification de PostgreSQL..."
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL n'est pas installé."
    echo ""
    echo "📋 Instructions d'installation PostgreSQL:"
    echo "=========================================="
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install postgresql postgresql-contrib python3-dev libpq-dev"
    echo ""
    echo "CentOS/RHEL:"
    echo "  sudo yum install postgresql postgresql-server postgresql-contrib postgresql-devel"
    echo ""
    echo "macOS:"
    echo "  brew install postgresql"
    echo ""
    echo "Puis relancez ce script."
    exit 1
fi

# 3. Démarrage du service PostgreSQL
print_status "Démarrage du service PostgreSQL..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start postgresql 2>/dev/null || print_warning "Impossible de démarrer PostgreSQL via systemctl"
elif command -v service &> /dev/null; then
    sudo service postgresql start 2>/dev/null || print_warning "Impossible de démarrer PostgreSQL via service"
elif command -v brew &> /dev/null; then
    brew services start postgresql 2>/dev/null || print_warning "Impossible de démarrer PostgreSQL via brew"
fi

# 4. Configuration automatique de la base de données
print_status "Configuration de la base de données PostgreSQL..."
python3 setup_postgresql.py
if [ $? -ne 0 ]; then
    print_error "Erreur lors de la configuration PostgreSQL"
    print_status "Configuration manuelle nécessaire:"
    echo "  sudo -u postgres createdb blogflow_db"
    echo "  sudo -u postgres psql -c \"CREATE USER blogflow_user WITH PASSWORD 'blogflow_password';\""
    echo "  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE blogflow_db TO blogflow_user;\""
    echo "  sudo -u postgres psql -c \"ALTER USER blogflow_user CREATEDB;\""
fi

# 5. Configuration de l'environnement Python
print_status "Configuration de l'environnement Python..."
if [ ! -d "../blog_env" ]; then
    print_status "Création de l'environnement virtuel..."
    python3 -m venv ../blog_env
fi

source ../blog_env/bin/activate
print_success "Environnement virtuel activé"

# 6. Installation des dépendances
print_status "Installation des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Dépendances installées"
else
    print_warning "Erreur lors de l'installation des dépendances"
fi

# 7. Vérification de la connexion PostgreSQL
print_status "Test de connexion PostgreSQL..."
export DATABASE_URL="postgresql://blogflow_user:blogflow_password@localhost:5432/blogflow_db"
python manage.py check --database default > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Connexion PostgreSQL établie"
else
    print_error "Impossible de se connecter à PostgreSQL"
    print_status "Vérifiez la configuration dans .env"
    exit 1
fi

# 8. Migrations et données
print_status "Application des migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    print_error "Erreur lors des migrations"
    exit 1
fi

# 9. Création des données de test
print_status "Vérification des données de test..."
ARTICLE_COUNT=$(python manage.py shell -c "from posts.models import Article; print(Article.objects.count())" 2>/dev/null | tail -n 1)
if [ "$ARTICLE_COUNT" -eq 0 ] 2>/dev/null; then
    print_status "Création des données de test..."
    python create_sample_data.py
    print_success "Données de test créées"
fi

# 10. Création de l'utilisateur admin
print_status "Vérification de l'utilisateur administrateur..."
ADMIN_EXISTS=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null | tail -n 1)

if [ "$ADMIN_EXISTS" != "True" ]; then
    echo ""
    echo "🔐 CRÉATION DE L'UTILISATEUR ADMINISTRATEUR"
    echo "============================================"
    echo "Username: admin"
    echo "Email: admin@blogflow.local"
    echo "Password: admin123"
    echo "============================================"
    echo ""
    
    python manage.py shell -c "
from accounts.models import User

admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@blogflow.local',
        'first_name': 'Administrateur',
        'last_name': 'BlogFlow',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'role': 'admin',
        'bio': 'Administrateur principal du blog BlogFlow',
        'display_name': 'Admin BlogFlow'
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print('✅ Utilisateur administrateur créé')
"
fi

# 11. Collecte des fichiers statiques
print_status "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput > /dev/null 2>&1

# 12. Informations finales
echo ""
echo "🎉 CONFIGURATION POSTGRESQL TERMINÉE"
echo "===================================="
echo ""
echo "🌐 ACCÈS AU PROJET"
echo "• Site web: http://127.0.0.1:8000"
echo "• Administration: http://127.0.0.1:8000/admin"
echo "• API REST: http://127.0.0.1:8000/api/v1/"
echo ""
echo "🔐 CONNEXION ADMINISTRATEUR"
echo "• Username: admin"
echo "• Password: admin123"
echo ""
echo "🐘 BASE DE DONNÉES POSTGRESQL"
echo "• Base: blogflow_db"
echo "• Utilisateur: blogflow_user"
echo "• Password: blogflow_password"
echo ""

# 13. Démarrage du serveur
print_success "Démarrage du serveur Django avec PostgreSQL..."
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""
python manage.py runserver 8000