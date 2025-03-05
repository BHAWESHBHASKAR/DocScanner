import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Get base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database", "data", "document_scanner.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this in production
    
    # API Keys
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-r1-distill-llama-70b:free')
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
