#!/bin/bash

echo "🚀 Démarrage du projet BlogFlow Django..."
echo "========================================="

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction d'affichage coloré
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
    print_error "Fichier manage.py non trouvé. Assurez-vous d'être dans le répertoire du projet Django."
    exit 1
fi

# Activation de l'environnement virtuel
print_status "Activation de l'environnement virtuel..."
if [ -f "../blog_env/bin/activate" ]; then
    source ../blog_env/bin/activate
    print_success "Environnement virtuel activé"
else
    print_error "Environnement virtuel non trouvé dans ../blog_env/"
    print_status "Création de l'environnement virtuel..."
    python3 -m venv ../blog_env
    source ../blog_env/bin/activate
    pip install -r requirements.txt
    print_success "Environnement virtuel créé et dépendances installées"
fi

# Démarrage de PostgreSQL si nécessaire
print_status "Vérification de PostgreSQL..."
if command -v service >/dev/null 2>&1; then
    if service postgresql status > /dev/null 2>&1; then
        print_success "PostgreSQL est déjà en cours d'exécution"
    else
        print_status "Tentative de démarrage de PostgreSQL..."
        if command -v sudo >/dev/null 2>&1; then
            sudo service postgresql start 2>/dev/null || print_warning "Impossible de démarrer PostgreSQL (pas de sudo ou service non disponible)"
        else
            service postgresql start 2>/dev/null || print_warning "Impossible de démarrer PostgreSQL (pas de sudo ou service non disponible)"
        fi
        sleep 2
    fi
elif command -v brew >/dev/null 2>&1; then
    # macOS avec Homebrew
    if brew services list | grep postgresql | grep started > /dev/null; then
        print_success "PostgreSQL est déjà en cours d'exécution (Homebrew)"
    else
        print_status "Démarrage de PostgreSQL via Homebrew..."
        brew services start postgresql
        sleep 2
    fi
else
    print_warning "PostgreSQL: utilisation de SQLite par défaut"
fi

# Vérification des dépendances
print_status "Vérification des dépendances Python..."
python -c "import django, psycopg2" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Dépendances principales disponibles"
else
    print_warning "Installation des dépendances manquantes..."
    pip install -r requirements.txt
fi

# Application des migrations
print_status "Application des migrations..."
python manage.py migrate
if [ $? -eq 0 ]; then
    print_success "Migrations appliquées avec succès"
else
    print_error "Erreur lors de l'application des migrations"
    exit 1
fi

# Création des données de test si nécessaire
print_status "Vérification des données de test..."
ARTICLE_COUNT=$(python manage.py shell -c "from posts.models import Article; print(Article.objects.count())" 2>/dev/null | tail -n 1)
if [ "$ARTICLE_COUNT" -eq 0 ] 2>/dev/null; then
    print_status "Création des données de test..."
    python create_sample_data.py
    print_success "Données de test créées"
else
    print_success "$ARTICLE_COUNT articles trouvés en base"
fi

# Vérification et création d'un utilisateur administrateur
print_status "Vérification de l'utilisateur administrateur..."
ADMIN_EXISTS=$(python manage.py shell -c "from accounts.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null | tail -n 1)

if [ "$ADMIN_EXISTS" = "True" ]; then
    print_success "Utilisateur administrateur existant trouvé"
    # Afficher les infos des admins existants
    echo ""
    echo "👤 Utilisateurs administrateurs existants :"
    python manage.py shell -c "
from accounts.models import User
admins = User.objects.filter(is_superuser=True)
for admin in admins:
    print(f'   - Username: {admin.username} | Email: {admin.email}')
"
else
    print_status "Création d'un utilisateur administrateur..."
    echo ""
    echo "🔐 INFORMATIONS DE CONNEXION ADMINISTRATEUR"
    echo "==========================================="
    echo "Username: admin"
    echo "Email: admin@blogflow.local"
    echo "Password: admin123"
    echo "==========================================="
    echo ""
    
    # Créer l'utilisateur admin
    python manage.py shell -c "
from accounts.models import User

# Créer ou récupérer l'utilisateur admin
try:
    admin_user = User.objects.get(username='admin')
    print('ℹ️  Utilisateur admin existe déjà')
    # Mettre à jour le mot de passe pour être sûr
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    if hasattr(admin_user, 'role'):
        admin_user.role = 'admin'
    admin_user.save()
    print('🔄 Mot de passe admin mis à jour: admin123')
except User.DoesNotExist:
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@blogflow.local',
        password='admin123',
        first_name='Administrateur',
        last_name='BlogFlow',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    if hasattr(admin_user, 'role'):
        admin_user.role = 'admin'
        admin_user.bio = 'Administrateur principal du blog BlogFlow'
        admin_user.display_name = 'Admin BlogFlow'
        admin_user.save()
    print('✅ Utilisateur administrateur créé avec succès')

print(f'👤 Admin: {admin_user.username} | Email: {admin_user.email}')
"
    print_success "Utilisateur administrateur configuré"
fi

# Collecte des fichiers statiques
print_status "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Fichiers statiques collectés"
else
    print_warning "Erreur lors de la collecte des fichiers statiques (non critique)"
fi

# Affichage des informations de connexion
echo ""
echo "🌐 ACCÈS AU PROJET"
echo "=================="
echo "• Site web: http://127.0.0.1:8000"
echo "• Administration: http://127.0.0.1:8000/admin"
echo "• API REST: http://127.0.0.1:8000/api/v1/"
echo ""
echo "📊 STATISTIQUES"
echo "==============="
python manage.py shell -c "
from posts.models import Article, Category, Tag
from accounts.models import User
print(f'• Articles: {Article.objects.count()}')
print(f'• Catégories: {Category.objects.count()}')
print(f'• Tags: {Tag.objects.count()}')
print(f'• Utilisateurs: {User.objects.count()}')
"
echo ""

# Démarrage du serveur
print_success "Démarrage du serveur Django..."
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""
python manage.py runserver 8000