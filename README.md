# Document Scanner - AI-Powered Document Similarity Detection

A modern web application that uses AI to detect similarities between documents, helping users identify duplicates and related content. Built with Flask, SQLAlchemy, and powered by DeepSeek and Mistral AI models.

## 🎥 Demo

https://user-images.githubusercontent.com/assets/cec76d33-fe0b-444d-85c4-23d62d6988ff

![Demo Video](https://user-images.githubusercontent.com/assets/cec76d33-fe0b-444d-85c4-23d62d6988ff)

Watch the demo video above to see how to use the application.

## ✨ Features

- AI-Powered Document Analysis: Uses DeepSeek and Mistral AI models for semantic understanding
- Multiple Similarity Detection Methods:
  - AI-based semantic analysis
  - Traditional text similarity algorithms
  - Content hash matching for exact duplicates
- Support for Multiple File Types:
  - PDF documents
  - Word documents (DOC, DOCX)
  - Text files (TXT)
- Credit System:
  - 20 free credits daily for each user
  - Request additional credits from administrators
  - Credit tracking and management
- User Management:
  - User registration and authentication
  - Admin dashboard for user management
  - Role-based access control
- Document Management:
  - Secure document upload and storage
  - Document preview and comparison
  - Match history tracking
- Modern UI/UX:
  - Responsive design
  - Real-time feedback
  - Interactive visualizations for similarity scores

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- API keys for OpenRouter (DeepSeek) and Mistral AI

### API Keys Setup

#### OpenRouter (for DeepSeek AI) API Key:
1. Go to [OpenRouter.ai](https://openrouter.ai/) and create an account
2. After logging in, navigate to the API Keys section
3. Click "Create API Key" and give it a name related to this project
4. Copy the generated API key (starts with "sk-or-v1-...")
5. Add this key to your `.env` file as `OPENROUTER_API_KEY`

#### Mistral AI API Key:
1. Visit [Mistral AI Platform](https://console.mistral.ai/) and create an account
2. Go to the API section in your dashboard
3. Generate a new API key
4. Copy the API key (starts with a unique identifier)
5. Add this key to your `.env` file as `MISTRAL_API_KEY`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BHAWESHBHASKAR/DocScanner.git
   cd DocScanner
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   ```
   Update the following variables in `.env`:
   - SECRET_KEY: Your Flask secret key (a random string for security)
   - OPENROUTER_API_KEY: Your OpenRouter API key from the steps above
   - MISTRAL_API_KEY: Your Mistral AI API key from the steps above

5. Initialize the database:
   ```bash
   python db_management.py migrate
   ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Access the application at `http://localhost:5003`

### Default Admin Account

- Username: admin
- Password: admin
- Email: admin@example.com

Note: Please change these credentials after first login

## 💡 How to Use

1. Register/Login:
   - Create a new account or login with existing credentials
   - Each new user gets 20 free credits daily

2. Upload Documents:
   - Click "Scan Document" in the navigation
   - Select a document to upload (PDF, DOC, DOCX, or TXT)
   - Each scan costs 1 credit

3. View Results:
   - See similarity scores for matched documents
   - View detailed comparison between documents
   - Check match history in your profile

4. Request Credits:
   - Request additional credits when needed
   - Provide reason for credit request
   - Wait for admin approval

5. Admin Features:
   - Manage users and credit requests
   - View system analytics
   - Configure system settings

## 🔧 API Documentation

### Authentication

All API endpoints require authentication. Use the following header:
```
Authorization: Bearer <your-token>
```

### Endpoints

#### Document Upload
```http
POST /document/upload
Content-Type: multipart/form-data

file: <document_file>
```

#### Get Document Matches
```http
GET /document/matches/<document_id>
```

#### Request Credits
```http
POST /credit/request
Content-Type: application/json

{
  "amount": number,
  "reason": string
}
```

For complete API documentation, see the [API Documentation](docs/API.md).

## 🛠️ Technology Stack

- Backend:
  - Flask (Python web framework)
  - SQLAlchemy (ORM)
  - Flask-Login (Authentication)
  - APScheduler (Background tasks)

- AI/ML:
  - DeepSeek AI (Semantic analysis)
  - Mistral AI (Text comparison)
  - scikit-learn (Traditional similarity)

- Frontend:
  - HTML5/CSS3
  - JavaScript
  - Modern UI components
  - Responsive design

- Database:
  - SQLite (Development)
  - Supports PostgreSQL (Production)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 👥 Authors

- Bhawesh Bhaskar - Initial work - [BHAWESHBHASKAR](https://github.com/BHAWESHBHASKAR)

## 📞 Contact

- LinkedIn: [bhawesh-bhaskar](https://www.linkedin.com/in/bhawesh-bhaskar)
- GitHub: [BHAWESHBHASKAR](https://github.com/BHAWESHBHASKAR)
- Email: bhaskarbhawesh09@gmail.com

## 📋 Sample Documents and Testing

The repository includes sample documents in the `sample_documents` directory to help you test the similarity detection features:

### Test Documents:
1. `ai_doc1.txt` and `ai_doc2.txt`:
   - Similar documents about artificial intelligence
   - Expected similarity score: ~70-80%
   - Use these to test semantic similarity detection

2. `climate_doc.txt`:
   - Different topic (climate change)
   - Expected similarity score with AI docs: <30%
   - Use this to verify dissimilar content detection

### Quick Testing Steps:
1. After setting up the application:
   - Login with admin credentials
   - Upload `ai_doc1.txt`
   - Then upload `ai_doc2.txt`
   - You should see a high similarity score
   - Upload `climate_doc.txt` to verify low similarity detection

2. Testing Features:
   - Document comparison view
   - Similarity scores
   - Match highlighting
   - Credit system functionality

### Expected Results:
- High similarity between AI documents demonstrates semantic matching
- Low similarity with climate document shows accurate differentiation
- System should identify key phrases and concepts
- Match details should show relevant text comparisons

## 🧪 Test Credentials

For testing purposes, use these credentials:

### Admin Account:
- Username: admin
- Password: admin
- Email: admin@example.com

### Regular User Account:
- Username: testuser
- Password: testpass123
- Email: test@example.com


