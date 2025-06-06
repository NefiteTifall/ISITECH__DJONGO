#!/usr/bin/env python3
"""
Script de configuration automatique PostgreSQL pour BlogFlow
Crée automatiquement la base de données et l'utilisateur nécessaires
"""
import os
import sys
import subprocess
import getpass

def run_command(command, description, check=True):
    """Exécute une commande shell avec gestion d'erreurs"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Erreur: {result.stderr}")
            return False
        print(f"✅ {description} - Succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de {description}: {e}")
        return False

def main():
    print("🐘 Configuration automatique PostgreSQL pour BlogFlow")
    print("=" * 55)
    
    # Vérifier si PostgreSQL est installé
    if not run_command("which psql", "Vérification de l'installation PostgreSQL", check=False):
        print("""
❌ PostgreSQL n'est pas installé ou non accessible.

Installation selon votre système:
• Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib python3-dev libpq-dev
• CentOS/RHEL: sudo yum install postgresql postgresql-server postgresql-contrib postgresql-devel
• macOS: brew install postgresql
• Windows: Télécharger depuis https://www.postgresql.org/download/windows/
        """)
        return False
    
    # Vérifier si PostgreSQL fonctionne
    if not run_command("sudo systemctl status postgresql", "Vérification du service PostgreSQL", check=False):
        if not run_command("sudo systemctl start postgresql", "Démarrage de PostgreSQL"):
            print("⚠️  Impossible de démarrer PostgreSQL automatiquement")
    
    # Configuration de la base de données
    print("\n📊 Configuration de la base de données...")
    
    db_commands = [
        "sudo -u postgres createdb blogflow_db 2>/dev/null || echo 'Base blogflow_db existe déjà'",
        "sudo -u postgres psql -c \"CREATE USER blogflow_user WITH PASSWORD 'blogflow_password';\" 2>/dev/null || echo 'Utilisateur blogflow_user existe déjà'",
        "sudo -u postgres psql -c \"ALTER ROLE blogflow_user SET client_encoding TO 'utf8';\"",
        "sudo -u postgres psql -c \"ALTER ROLE blogflow_user SET default_transaction_isolation TO 'read committed';\"",
        "sudo -u postgres psql -c \"ALTER ROLE blogflow_user SET timezone TO 'UTC';\"",
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE blogflow_db TO blogflow_user;\"",
        "sudo -u postgres psql -c \"ALTER USER blogflow_user CREATEDB;\"",
    ]
    
    success = True
    for cmd in db_commands:
        if not run_command(cmd, f"Exécution: {cmd.split(';')[0].split('\"')[1] if '\"' in cmd else cmd}", check=False):
            success = False
    
    if success:
        print("\n✅ Configuration PostgreSQL terminée avec succès!")
        print("\n📋 INFORMATIONS DE CONNEXION:")
        print("=" * 35)
        print("• Base de données: blogflow_db")
        print("• Utilisateur: blogflow_user")
        print("• Mot de passe: blogflow_password")
        print("• Host: localhost")
        print("• Port: 5432")
        print("=" * 35)
        
        print("\n🔧 Étapes suivantes:")
        print("1. Copiez le fichier .env.example vers .env")
        print("2. Modifiez les paramètres DATABASE_URL dans .env")
        print("3. Lancez: ./start.sh")
        
        return True
    else:
        print("\n❌ Erreurs lors de la configuration PostgreSQL")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")