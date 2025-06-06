def theme_context(request):
    """Context processor pour le thème sombre/clair"""
    theme = request.session.get('theme', 'light')
    return {
        'current_theme': theme,
        'is_dark_theme': theme == 'dark'
    }

def site_info(request):
    """Informations générales du site"""
    return {
        'site_name': 'BlogFlow',
        'site_description': 'Blog académique universitaire',
        'current_year': 2025,
    }