import requests
import json
from flask import current_app

class AIService:
    @staticmethod
    def compare_with_openrouter(text1, text2):
        """Compare two texts using OpenRouter's Deepseek model"""
        headers = {
            "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
            "HTTP-Referer": "http://localhost:5001",
            "Content-Type": "application/json"
        }
        
        # Create a prompt that asks for similarity comparison
        prompt = f"""Compare the similarity between these two texts and return a similarity score between 0 and 1, where 1 means identical and 0 means completely different. Only return the number, no other text.

Text 1:
{text1}

Text 2:
{text2}

Similarity score:"""
        
        data = {
            "model": current_app.config['OPENROUTER_MODEL'],
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Extract just the number from the response
                content = response.json()['choices'][0]['message']['content'].strip()
                try:
                    score = float(content)
                    return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
                except ValueError:
                    return None
        except Exception as e:
            current_app.logger.error(f"OpenRouter API error: {str(e)}")
            return None

    @staticmethod
    def compare_with_mistral(text1, text2):
        """Compare two texts using Mistral AI"""
        headers = {
            "Authorization": f"Bearer {current_app.config['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        # Create a prompt that asks for similarity comparison
        prompt = f"""Compare the similarity between these two texts and return a similarity score between 0 and 1, where 1 means identical and 0 means completely different. Only return the number, no other text.

Text 1:
{text1}

Text 2:
{text2}

Similarity score:"""
        
        data = {
            "model": "mistral-tiny",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Extract just the number from the response
                content = response.json()['choices'][0]['message']['content'].strip()
                try:
                    score = float(content)
                    return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
                except ValueError:
                    return None
        except Exception as e:
            current_app.logger.error(f"Mistral API error: {str(e)}")
            return None
