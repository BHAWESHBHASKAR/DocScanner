# Document Scanner - AI-Powered Document Similarity Detection

A modern web application that uses AI to detect similarities between documents, helping users identify duplicates and related content. Built with Flask, SQLAlchemy, and powered by DeepSeek and Mistral AI models.

## 🎥 Demo

https://github.com/BHAWESHBHASKAR/DocScanner/blob/main/.github/assets/demo.mp4

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

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/document-scanner.git
   cd document-scanner
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
   - SECRET_KEY: Your Flask secret key
   - OPENROUTER_API_KEY: Your OpenRouter API key
   - MISTRAL_API_KEY: Your Mistral AI API key

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👥 Authors

- Bhawesh Bhaskar - Initial work - [BHAWESHBHASKAR](https://github.com/BHAWESHBHASKAR)

## 📞 Contact

- LinkedIn: [bhawesh-bhaskar](https://www.linkedin.com/in/bhawesh-bhaskar)
- GitHub: [BHAWESHBHASKAR](https://github.com/BHAWESHBHASKAR)
- Email: bhaskarbhawesh09@gmail.com

