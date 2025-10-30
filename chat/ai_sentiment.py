"""
AI Sentiment Analysis pour le système de chat SmartCampus
Analyse le sentiment des messages en temps réel
"""
from transformers import pipeline
import torch

class SentimentAnalyzer:
    """Analyseur de sentiment pour les messages de chat"""
    
    def __init__(self):
        """Initialise le modèle de sentiment"""
        # Forcer l'utilisation du CPU (device -1)
        # Ne pas utiliser device="meta" qui cause des erreurs
        self.device = -1  # Toujours CPU pour éviter les problèmes de device
        
        # Charger le modèle pré-entraîné pour l'analyse de sentiment
        # Utilise un modèle plus léger pour la production
        try:
            import os
            # IMPORTANT: Désactiver COMPLÈTEMENT le device meta de PyTorch
            os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            # Désactiver explicitement le lazy loading dans PyTorch
            torch.set_default_dtype(torch.float32)
            
            self.analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self.device,
                framework="pt",
                model_kwargs={
                    "low_cpu_mem_usage": False,
                    "torch_dtype": torch.float32
                }
            )
            print("✅ Modèle d'analyse de sentiment chargé avec succès (CPU)")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            self.analyzer = None
    
    def analyze_message(self, text):
        """
        Analyse le sentiment d'un message
        
        Args:
            text (str): Le texte du message à analyser
            
        Returns:
            dict: {
                'sentiment': 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL',
                'score': float (0-1),
                'emoji': str
            }
        """
        if not self.analyzer or not text or len(text.strip()) == 0:
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.5,
                'emoji': '😐'
            }
        
        try:
            # Limiter la longueur du texte pour éviter les dépassements
            text = text[:512]
            
            result = self.analyzer(text)[0]
            
            sentiment = result['label']
            score = result['score']
            
            # Mapper les sentiments aux émojis
            emoji_map = {
                'POSITIVE': '😊' if score > 0.8 else '🙂',
                'NEGATIVE': '😞' if score > 0.8 else '😕',
                'NEUTRAL': '😐'
            }
            
            return {
                'sentiment': sentiment,
                'score': score,
                'emoji': emoji_map.get(sentiment, '😐')
            }
            
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.5,
                'emoji': '😐'
            }
    
    def analyze_batch(self, messages):
        """
        Analyse un lot de messages
        
        Args:
            messages (list): Liste de textes à analyser
            
        Returns:
            list: Liste de résultats d'analyse
        """
        if not self.analyzer:
            return [self.analyze_message(msg) for msg in messages]
        
        try:
            # Nettoyer et limiter les messages
            cleaned_messages = [msg[:512] for msg in messages if msg and len(msg.strip()) > 0]
            
            if not cleaned_messages:
                return []
            
            results = self.analyzer(cleaned_messages)
            
            analyzed = []
            for result in results:
                sentiment = result['label']
                score = result['score']
                
                emoji_map = {
                    'POSITIVE': '😊' if score > 0.8 else '🙂',
                    'NEGATIVE': '😞' if score > 0.8 else '😕',
                    'NEUTRAL': '😐'
                }
                
                analyzed.append({
                    'sentiment': sentiment,
                    'score': score,
                    'emoji': emoji_map.get(sentiment, '😐')
                })
            
            return analyzed
            
        except Exception as e:
            print(f"Erreur lors de l'analyse par batch: {e}")
            return [self.analyze_message(msg) for msg in messages]
    
    def get_conversation_mood(self, messages):
        """
        Analyse l'ambiance générale d'une conversation
        
        Args:
            messages (list): Liste de messages de la conversation
            
        Returns:
            dict: Statistiques sur l'ambiance
        """
        if not messages:
            return {
                'overall_mood': 'NEUTRAL',
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0
            }
        
        analyses = self.analyze_batch(messages)
        
        total = len(analyses)
        positive = sum(1 for a in analyses if a['sentiment'] == 'POSITIVE')
        negative = sum(1 for a in analyses if a['sentiment'] == 'NEGATIVE')
        neutral = total - positive - negative
        
        # Déterminer l'ambiance générale
        if positive > negative and positive > neutral:
            overall = 'POSITIVE'
        elif negative > positive and negative > neutral:
            overall = 'NEGATIVE'
        else:
            overall = 'NEUTRAL'
        
        return {
            'overall_mood': overall,
            'positive_percentage': round((positive / total) * 100, 2),
            'negative_percentage': round((negative / total) * 100, 2),
            'neutral_percentage': round((neutral / total) * 100, 2),
            'total_messages': total
        }


# Instance globale (singleton)
_sentiment_analyzer = None

def get_sentiment_analyzer():
    """Récupère l'instance du sentiment analyzer (singleton)"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
