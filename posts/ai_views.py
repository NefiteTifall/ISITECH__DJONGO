"""
Vues pour l'intégration IA - Génération d'articles, résumés et images
"""
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import logging

from .ai_services import ai_generator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class GenerateArticleView(View):
    """Vue pour générer un article complet avec Gemini"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()
            
            if not prompt:
                return JsonResponse({
                    'success': False,
                    'error': 'Prompt requis pour générer un article'
                }, status=400)
            
            if len(prompt) < 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Le prompt doit contenir au moins 5 caractères'
                }, status=400)
            
            logger.info(f"📝 Génération d'article demandée par {request.user.username}: {prompt}")
            
            # Appel au service IA
            result = ai_generator.generate_article(prompt)
            
            if result['success']:
                logger.info(f"✅ Article généré avec succès pour: {prompt}")
                return JsonResponse(result)
            else:
                logger.error(f"❌ Échec génération article: {result.get('error', 'Erreur inconnue')}")
                return JsonResponse(result, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            logger.error(f"Erreur inattendue génération article: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class GenerateSummaryView(View):
    """Vue pour générer un résumé avec Gemini"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'error': 'Titre requis pour générer un résumé'
                }, status=400)
            
            logger.info(f"📄 Génération de résumé demandée par {request.user.username}: {title}")
            
            # Appel au service IA
            result = ai_generator.generate_summary(title, content)
            
            if result['success']:
                logger.info(f"✅ Résumé généré avec succès pour: {title}")
                return JsonResponse(result)
            else:
                logger.error(f"❌ Échec génération résumé: {result.get('error', 'Erreur inconnue')}")
                return JsonResponse(result, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            logger.error(f"Erreur inattendue génération résumé: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class GenerateImageView(View):
    """Vue pour générer une image avec DALL-E 3"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()
            
            if not prompt:
                return JsonResponse({
                    'success': False,
                    'error': 'Prompt requis pour générer une image'
                }, status=400)
            
            if len(prompt) < 3:
                return JsonResponse({
                    'success': False,
                    'error': 'Le prompt doit contenir au moins 3 caractères'
                }, status=400)
            
            logger.info(f"🖼️ Génération d'image demandée par {request.user.username}: {prompt}")
            
            # Appel au service IA
            result = ai_generator.generate_image(prompt)
            
            if result['success']:
                logger.info(f"✅ Image générée avec succès pour: {prompt}")
                return JsonResponse(result)
            else:
                logger.error(f"❌ Échec génération image: {result.get('error', 'Erreur inconnue')}")
                return JsonResponse(result, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            logger.error(f"Erreur inattendue génération image: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=500)


@login_required
def get_available_generators(request):
    """Retourne la liste des générateurs IA disponibles et leur statut"""
    try:
        status = ai_generator.get_status()
        
        generators = {
            'article': {
                'name': 'Générateur d\'articles (Gemini)',
                'description': 'Génère des articles complets avec structure, titre et contenu',
                'endpoint': '/ai/generate-article/',
                'available': status['gemini_available'],
                'provider': 'Google Gemini',
                'status': 'Opérationnel' if status['gemini_available'] else 'Indisponible'
            },
            'summary': {
                'name': 'Générateur de résumés (Gemini)',
                'description': 'Crée des résumés accrocheurs et professionnels',
                'endpoint': '/ai/generate-summary/',
                'available': status['gemini_available'],
                'provider': 'Google Gemini',
                'status': 'Opérationnel' if status['gemini_available'] else 'Indisponible'
            },
            'image': {
                'name': 'Générateur d\'images (DALL-E 3)',
                'description': 'Génère des images professionnelles pour vos articles',
                'endpoint': '/ai/generate-image/',
                'available': status['openai_available'],
                'provider': 'OpenAI DALL-E 3',
                'status': 'Opérationnel' if status['openai_available'] else 'Indisponible'
            }
        }
        
        return JsonResponse({
            'success': True,
            'generators': generators,
            'system_status': status
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération statut IA: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la vérification du statut des APIs IA'
        }, status=500)


# Vue pour les tests de diagnostic
@login_required
def ai_diagnostic(request):
    """Diagnostic des APIs IA - pour les administrateurs"""
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Accès réservé aux administrateurs'
        }, status=403)
    
    try:
        status = ai_generator.get_status()
        
        diagnostic = {
            'apis_status': status,
            'environment': {
                'gemini_key_set': bool(getattr(settings, 'GEMINI_API_KEY', None)),
                'openai_key_set': bool(getattr(settings, 'OPENAI_API_KEY', None)),
                'debug_mode': settings.DEBUG
            },
            'recommendations': []
        }
        
        # Recommandations basées sur le statut
        if not status['gemini_available']:
            if not status['gemini_key_configured']:
                diagnostic['recommendations'].append(
                    "Configurez votre clé API Gemini dans le fichier .env (GEMINI_API_KEY)"
                )
            else:
                diagnostic['recommendations'].append(
                    "Vérifiez votre clé API Gemini - elle semble invalide ou expirée"
                )
        
        if not status['openai_available']:
            if not status['openai_key_configured']:
                diagnostic['recommendations'].append(
                    "Configurez votre clé API OpenAI dans le fichier .env (OPENAI_API_KEY)"
                )
            else:
                diagnostic['recommendations'].append(
                    "Vérifiez votre clé API OpenAI - elle semble invalide ou sans quota suffisant"
                )
        
        if status['gemini_available'] and status['openai_available']:
            diagnostic['recommendations'].append(
                "🎉 Toutes les APIs IA sont opérationnelles !"
            )
        
        return JsonResponse({
            'success': True,
            'diagnostic': diagnostic
        })
        
    except Exception as e:
        logger.error(f"Erreur diagnostic IA: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du diagnostic: {str(e)}'
        }, status=500)