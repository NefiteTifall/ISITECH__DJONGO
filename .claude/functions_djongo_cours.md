## **JOUR 1 - FONDATIONS ET ARCHITECTURE**

### **1.1 Configuration Projet**

- [ ]  Créer un environnement virtuel Python
- [ ]  Installer Django 4.2+ et dépendances (PostgreSQL, Pillow)
- [ ]  Structurer le projet avec 4 apps : `blog`, `users`, `comments`, `analytics`
- [ ]  Configurer settings.py multi-environnements (dev/staging/prod)
- [ ]  Paramétrer PostgreSQL avec variables d'environnement
- [ ]  Configurer les fichiers statiques et médias

### **1.2 Système d'Authentification**

- [ ]  Modèle User personnalisé avec champs étendus
- [ ]  Système de rôles (Lecteur/Auteur/Éditeur/Admin)
- [ ]  Inscription/connexion/déconnexion basique
- [ ]  Reset password simple
- [ ]  Middleware de gestion des permissions

### **1.3 Configuration Avancée**

- [ ]  Logging simple
- [ ]  Middleware personnalisé pour analytics
- [ ]  Tests unitaires de base

---

## **JOUR 2 - MODÈLES ET BASE DE DONNÉES**

### **2.1 Modèles de Base**

- [ ]  **Modèle Category**
    - Nom, description, slug,  icône
    - Meta ordering et unique constraints
    - Méthode `get_absolute_url()`
    - Compteur d'articles dynamique
- [ ]  **Modèle Tag (SLUG)**
    - Nom,
    - Relation many-to-many avec articles
    - Méthode `get_popular_tags()`
- [ ]  **Modèle Article**
    - Titre, slug, contenu, extrait
    - Auteur (ForeignKey User), catégorie, tags
    - Statut (brouillon/publié/archivé)
    - Image de couverture, dates de création/modification
    - Compteurs (vues, likes)
    - Meta SEO (title, description)

### **2.2 Modèles Avancés**

- [ ]  **Modèle Comment**
    - Contenu, auteur, article,
    - Système de modération basique
- [ ]  **Modèle Like/Bookmark**
    - Relations utilisateur-article
    - Timestamps pour analytics


---

## **JOUR 3 - VUES ET LOGIQUE MÉTIER**

### **3.1 Vues Publiques**

- [ ]  **Page d'accueil**
    - Articles récents et populaires
    - Catégories avec statistiques
    - Auteurs populaires
- [ ]  **Liste des articles**
    - Pagination avec Django Paginator
    - Filtrage par catégorie, tag, auteur
    - Tri (récent, populaire, alphabétique)
    - Recherche full-text PostgreSQL
- [ ]  **Détail d'article**
    - Affichage complet
    - Articles similaires (algorithme)
    - Système de likes simple


### **3.2 Vues Utilisateur**

- [ ]  **Profil utilisateur basique**
    - Articles de l'auteur
    - Statistiques personnelles
    - Articles bookmarkés
- [ ]  **Dashboard auteur**
    - Mes articles (brouillons/publiés)
    - Statistiques détaillées
    - Commentaires reçus

### **3.3 Système de Recherche**

- [ ]  Recherche full-text avec PostgreSQL
- [ ]  Filtres avancés (date, catégorie, auteur)
- [ ]  Suggestions de recherche

### **3.4 API REST**

- [ ]  articles
- [ ]  (CRUD)pour commentaires
- [ ]  (CRUD)pour likes/bookmarks

**JOUR 4 - INTERFACE ET EXPÉRIENCE UTILISATEUR**

### **4.1 Templates Avancés**

- [ ]  **Système de templates modulaires**
    - Base template avec blocks
    - Includes réutilisables
    - Macros pour éléments répétitifs
- [ ]  **Tags et filtres personnalisés**
    - Formatage des dates relatives
    - Highlight des termes de recherche
    - Calculs de temps de lecture
- [ ]  **UX Avancée**
    - Mode sombre/clair persistant

### **4.4 Internationalisation**

- [ ]  Configuration i18n Django
- [ ]  Traduction des templates (FR/EN/ES)