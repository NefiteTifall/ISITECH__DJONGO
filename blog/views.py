from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def toggle_theme(request):
    """Bascule entre thème clair et sombre"""
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    request.session['theme'] = new_theme
    
    return JsonResponse({
        'status': 'success',
        'theme': new_theme
    })