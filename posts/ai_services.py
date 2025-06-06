"""
Services d'intégration IA pour la génération de contenu
"""
import os
import base64
import logging
from io import BytesIO
from typing import Dict, Optional
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Import des APIs IA
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """Générateur de contenu IA utilisant Gemini et OpenAI"""
    
    def __init__(self):
        # Configuration Gemini
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_available = True
                logger.info("✅ Gemini API configurée avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur configuration Gemini: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            logger.warning("⚠️ Gemini API non disponible")
        
        # Configuration OpenAI
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.openai_available = True
                logger.info("✅ OpenAI API configurée avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur configuration OpenAI: {e}")
                self.openai_available = False
        else:
            self.openai_available = False
            logger.warning("⚠️ OpenAI API non disponible")
    
    def generate_article(self, prompt: str) -> Dict:
        """
        Génère un article complet avec Gemini
        """
        if not self.gemini_available:
            return {
                'success': False,
                'error': 'API Gemini non disponible. Vérifiez votre clé API.'
            }
        
        try:
            # Prompt optimisé pour générer un article structuré
            full_prompt = f"""
            Génère un article de blog complet et professionnel sur le sujet suivant : "{prompt}"

            STRUCTURE REQUISE :
            1. Un titre accrocheur et professionnel
            2. Un résumé de 2-3 phrases (maximum 300 caractères)
            3. Un contenu structuré en Markdown avec :
               - Introduction engageante
               - 3-4 sections principales avec sous-titres
               - Exemples concrets et pratiques
               - Conclusion avec call-to-action
               - Minimum 800 mots

            CONTRAINTES :
            - Utilise uniquement la syntaxe Markdown (# ## ### **gras** *italique* etc.)
            - Ton professionnel mais accessible
            - Contenu original et informatif
            - Évite les liens externes
            - Français correct et fluide

            FORMAT DE RÉPONSE :
            [TITRE]
            Titre de l'article ici

            [RESUME]
            Résumé concis de l'article ici

            [CONTENU]
            # Titre de l'article

            ## Introduction
            [contenu introduction]

            ## Section 1
            [contenu section 1]

            ## Section 2
            [contenu section 2]

            ## Section 3
            [contenu section 3]

            ## Conclusion
            [contenu conclusion]
            """
            
            response = self.gemini_model.generate_content(full_prompt)
            
            if not response.text:
                return {
                    'success': False,
                    'error': 'Gemini n\'a pas généré de contenu'
                }
            
            # Parser la réponse
            content = response.text.strip()
            return self._parse_article_response(content, prompt)
            
        except Exception as e:
            logger.error(f"Erreur génération article Gemini: {e}")
            return {
                'success': False,
                'error': f'Erreur lors de la génération: {str(e)}'
            }
    
    def generate_summary(self, title: str, content: str = "") -> Dict:
        """
        Génère un résumé avec Gemini
        """
        if not self.gemini_available:
            return {
                'success': False,
                'error': 'API Gemini non disponible'
            }
        
        try:
            if content.strip():
                prompt = f"""
                Génère un résumé concis et accrocheur pour cet article :
                
                Titre : {title}
                Contenu : {content[:1000]}...
                
                CONTRAINTES :
                - Maximum 280 caractères
                - Style engageant et professionnel
                - Capture l'essence de l'article
                - Donne envie de lire
                - En français
                
                Réponds uniquement avec le résumé, sans préfixe ni explication.
                """
            else:
                prompt = f"""
                Génère un résumé accrocheur pour un article intitulé : "{title}"
                
                CONTRAINTES :
                - Maximum 280 caractères
                - Style engageant et professionnel
                - Donne envie de lire l'article
                - En français
                
                Réponds uniquement avec le résumé, sans préfixe ni explication.
                """
            
            response = self.gemini_model.generate_content(prompt)
            
            if not response.text:
                return {
                    'success': False,
                    'error': 'Gemini n\'a pas généré de résumé'
                }
            
            summary = response.text.strip()
            
            # Limiter à 280 caractères si nécessaire
            if len(summary) > 280:
                summary = summary[:277] + "..."
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Erreur génération résumé Gemini: {e}")
            return {
                'success': False,
                'error': f'Erreur lors de la génération du résumé: {str(e)}'
            }
    
    def generate_image(self, prompt: str) -> Dict:
        """
        Génère une image avec DALL-E 3
        """
        if not self.openai_available:
            return {
                'success': False,
                'error': 'API OpenAI non disponible. Vérifiez votre clé API.'
            }
        
        try:
            # Améliorer le prompt pour de meilleures images
            enhanced_prompt = f"""
            Create a professional, high-quality image for a blog article about: {prompt}
            
            Style: Modern, clean, professional blog header image
            Requirements: 
            - Horizontal format (16:9 ratio)
            - High contrast and readability
            - Professional color scheme
            - No text or watermarks
            - Suitable for web publication
            - Visually appealing and relevant to the topic
            """
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1792x1024",  # Format 16:9 optimal pour blog
                quality="standard",
                n=1,
                response_format="b64_json"
            )
            
            if not response.data:
                return {
                    'success': False,
                    'error': 'DALL-E n\'a pas généré d\'image'
                }
            
            # Récupérer l'image en base64
            image_data = response.data[0]
            image_b64 = image_data.b64_json
            
            # Générer un nom de fichier unique
            import uuid
            filename = f"dalle_generated_{uuid.uuid4().hex[:8]}.png"
            
            # Décoder et sauvegarder l'image
            try:
                image_binary = base64.b64decode(image_b64)
                
                # Sauvegarder dans le système de fichiers Django
                image_file = ContentFile(image_binary, name=filename)
                saved_path = default_storage.save(f'ai_generated/{filename}', image_file)
                
                # URL complète de l'image
                image_url = default_storage.url(saved_path)
                
                return {
                    'success': True,
                    'type': 'generated_image',
                    'image_url': image_url,
                    'image_data': image_b64,
                    'filename': filename,
                    'alt_text': f'Image générée par IA : {prompt}',
                    'saved_path': saved_path
                }
                
            except Exception as save_error:
                logger.error(f"Erreur sauvegarde image: {save_error}")
                # Fallback : retourner juste les données base64
                return {
                    'success': True,
                    'type': 'generated_image',
                    'image_data': image_b64,
                    'filename': filename,
                    'alt_text': f'Image générée par IA : {prompt}'
                }
            
        except Exception as e:
            logger.error(f"Erreur génération image DALL-E: {e}")
            
            # Messages d'erreur spécifiques
            error_message = str(e)
            if "insufficient_quota" in error_message:
                error_message = "Quota OpenAI insuffisant. Vérifiez votre compte OpenAI."
            elif "invalid_api_key" in error_message:
                error_message = "Clé API OpenAI invalide. Vérifiez votre configuration."
            elif "content_policy_violation" in error_message:
                error_message = "Le prompt viole la politique de contenu d'OpenAI. Essayez un autre sujet."
            
            return {
                'success': False,
                'error': f'Erreur DALL-E: {error_message}'
            }
    
    def _parse_article_response(self, content: str, original_prompt: str) -> Dict:
        """
        Parse la réponse de Gemini pour extraire titre, résumé et contenu
        """
        try:
            lines = content.split('\n')
            
            titre = ""
            resume = ""
            contenu = ""
            
            current_section = None
            content_lines = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('[TITRE]'):
                    current_section = 'titre'
                    continue
                elif line.startswith('[RESUME]'):
                    current_section = 'resume'
                    continue
                elif line.startswith('[CONTENU]'):
                    current_section = 'contenu'
                    continue
                
                if current_section == 'titre' and line and not titre:
                    titre = line
                elif current_section == 'resume' and line and not resume:
                    resume = line
                elif current_section == 'contenu' and line:
                    content_lines.append(line)
            
            # Construire le contenu
            contenu = '\n'.join(content_lines).strip()
            
            # Fallback si le parsing a échoué
            if not titre or not contenu:
                # Essayer un parsing plus simple
                if content.startswith('#'):
                    lines = content.split('\n')
                    titre = lines[0].replace('#', '').strip()
                    contenu = '\n'.join(lines[1:]).strip()
                else:
                    titre = f"Article sur : {original_prompt}"
                    contenu = content
            
            if not resume:
                resume = f"Découvrez notre guide complet sur {original_prompt.lower()}."
            
            # Nettoyer et valider
            titre = titre[:200] if titre else f"Guide : {original_prompt}"
            resume = resume[:300] if resume else f"Article détaillé sur {original_prompt}"
            
            return {
                'success': True,
                'data': {
                    'titre': titre,
                    'resume': resume,
                    'contenu': contenu or f"# {titre}\n\nContenu en cours de génération..."
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur parsing réponse: {e}")
            return {
                'success': True,
                'data': {
                    'titre': f"Guide : {original_prompt}",
                    'resume': f"Article détaillé sur {original_prompt}",
                    'contenu': content  # Contenu brut en fallback
                }
            }
    
    def get_status(self) -> Dict:
        """
        Retourne le statut des APIs
        """
        return {
            'gemini_available': self.gemini_available,
            'openai_available': self.openai_available,
            'gemini_key_configured': bool(getattr(settings, 'GEMINI_API_KEY', None)),
            'openai_key_configured': bool(getattr(settings, 'OPENAI_API_KEY', None))
        }


# Instance globale
ai_generator = AIContentGenerator()