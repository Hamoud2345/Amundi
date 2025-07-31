# Django LangGraph Chatbot

A Django-based AI chatbot that uses LangGraph for intelligent routing and OpenAI for natural language processing. The chatbot can answer questions about companies stored in a database with fuzzy matching capabilities.

## Features

- 🤖 **AI-Powered Chatbot**: Uses OpenAI GPT models for intelligent responses
- 🔀 **Smart Routing**: LangGraph-based routing system that intelligently routes queries to company database or general chat
- 🏢 **Company Database**: Store and query company information with fuzzy matching
- 📊 **Chat History**: Persistent chat sessions with history tracking
- 📁 **CSV Upload**: Bulk import company data from CSV files
- 🎨 **Modern UI**: Clean, responsive web interface built with Tailwind CSS and Alpine.js
- 🔍 **Fuzzy Search**: Advanced company name matching using difflib for typos and variations

## Architecture

- **Backend**: Django REST Framework
- **AI Framework**: LangGraph + LangChain + OpenAI
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: HTML + Tailwind CSS + Alpine.js
- **Routing**: LLM-based intelligent query routing

## Project Structure

```
├── agent/                  # LangGraph agent and tools
│   ├── langgraph_agent.py # Main agent with LLM-based router
│   ├── tools.py           # Company lookup tool with fuzzy matching
│   └── llm_factory.py     # LLM factory (OpenAI/Fake)
├── companies/             # Django app for company management
│   ├── models.py          # Company and ChatHistory models
│   ├── views.py           # API endpoints and web views
│   ├── serializers.py     # DRF serializers
│   └── admin.py           # Django admin configuration
├── templates/             # HTML templates
│   ├── chat.html          # Main chat interface
│   ├── companies.html     # Company directory
│   ├── upload.html        # CSV upload interface
│   └── history.html       # Chat history viewer
├── the_agent/             # Django project settings
│   ├── settings.py        # Django configuration
│   └── urls.py            # URL routing
└── manage.py              # Django management script
```

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (optional - uses fake LLM for testing if not provided)
- All dependencies are listed in `requirements.txt` including `python-dotenv` for secure environment variable management

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd django-langgraph-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # Replace 'your-openai-api-key-here' with your actual API key
   ```
   
   Your `.env` file should look like:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main chat interface: http://127.0.0.1:8000/
   - Company directory: http://127.0.0.1:8000/companies/
   - CSV upload: http://127.0.0.1:8000/upload/
   - Chat history: http://127.0.0.1:8000/history/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Web Interface

1. **Chat Interface**: Ask questions about companies or general topics
2. **Company Directory**: Browse stored companies and ask AI questions about them
3. **CSV Upload**: Bulk import company data
4. **Chat History**: View previous conversations

### API Endpoints

- `POST /chat/` - Send messages to the chatbot
- `GET|POST /api/companies/` - List or create companies
- `POST /upload-csv/` - Upload CSV file with company data
- `GET /chat-history/` - Retrieve chat history

### Example API Usage

```bash
# Chat with the bot
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Acme Corp?"}'

# Add a company
curl -X POST http://127.0.0.1:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "description": "Global leader in widgets",
    "sector": "Manufacturing",
    "financials": {"revenue": "5B$", "employees": 12000}
  }'
```

### CSV Upload Format

Upload CSV files with the following columns:
```csv
name,description,sector,financials
Acme Corp,Global leader in widgets,Manufacturing,"{""revenue"": ""5B$"", ""employees"": 12000}"
```

## How It Works

### LangGraph Agent Architecture

1. **Router Node**: Uses LLM to classify queries as `company_query` or `general_query`
2. **Company Tool Node**: Extracts company names and searches database with fuzzy matching
3. **Chat Node**: Handles general conversation using OpenAI

### Fuzzy Matching

The company lookup tool uses multiple strategies:
1. Exact case-insensitive match
2. Substring matching (`icontains`)
3. Fuzzy matching using `difflib.SequenceMatcher` (75% similarity threshold)

## Configuration

### Environment Variables

Environment variables are loaded from a `.env` file in the project root using `python-dotenv`:

- `OPENAI_API_KEY`: Your OpenAI API key (optional - uses fake LLM if not set)
- `DEBUG`: Django debug mode (default: True)
- `SECRET_KEY`: Django secret key (auto-generated)

**Security Note**: The `.env` file is ignored by Git to protect your API keys. Use `.env.example` as a template.

### Django Settings

Key settings in `the_agent/settings.py`:
- Database configuration
- OpenAI API key loading
- CORS and CSRF settings for API access

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Missing .env file**: Copy `.env.example` to `.env` and add your OpenAI API key
2. **OpenAI API errors**: Check your API key in `.env` file and ensure you have credits
3. **403 Forbidden on API calls**: CSRF protection is disabled for API endpoints
4. **Company not found**: Try different variations of the company name (fuzzy matching should help)
5. **Environment variables not loading**: Ensure `python-dotenv` is installed (`pip install python-dotenv`)

### Debug Mode

The application includes debug logging for the LangGraph agent. Check the console output for:
- Router decisions
- Company name extraction
- Tool results

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Uses [LangChain](https://github.com/langchain-ai/langchain) for LLM integration
- UI components from [Tailwind CSS](https://tailwindcss.com/)
- Interactive features powered by [Alpine.js](https://alpinejs.dev/)
