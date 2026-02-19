# Cricnews-bot 🏏

A conversational cricket news assistant built with Streamlit and powered by Gemini models. Get live scores, match results, upcoming tournament information, and deep-dive cricket trivia in one place.

## Features ✨

- **Live Match Updates**: Real-time scores and status for ongoing matches.
- **Series & Tournament Tracking**: Comprehensive view of current and upcoming series (including World Cups, IPL, etc.).
- **Historical Results**: Fetch past match outcomes with a broad search context.
- **Cricket Specialist AI**: Powered by Gemini 2.5 Flash Lite with specialized prompt engineering to handle cricket-specific queries and famous players like Virat Kohli.
- **Modern Architecture**: Clean, modular structure with a single entry point.
- **Poetry Integration**: Robust dependency management and environment handling.

## Project Structure 📁

```text
Cricnews-bot/
├── main.py                 # Root entry point
├── app/                    # Core application logic
│   ├── config.py           # Configuration & Environment loading
│   ├── logger.py           # Logging setup
│   └── services/           # External API & LLM services
│       ├── cricket_service.py
│       └── llm_service.py
├── ui/                     # Streamlit UI components
│   └── streamlit_app.py
├── .env                    # Environment variables (API Keys & Prompt)
├── pyproject.toml          # Poetry configuration
└── README.md               # You are here!
```

## Setup & Installations 🚀

### 1. Prerequisites
- Python 3.12 or higher.
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management.

### 2. Clone and Install
```bash
git clone https://github.com/Nikhil-Maheshwari-10/Cricnews-bot.git
cd Cricnews-bot
poetry install
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
# Cricket API Key from cricketdata.org
CRICKETDATA_API_KEY=your_cricketdata_api_key

# Gemini API Key for LLM
GEMINI_API_KEY=your_gemini_api_key

# Model Selection (Optional: defaults to gemini-2.5-flash-lite)
LLM_MODEL="your_model"

# System Prompt (Optional: uses internal default if omitted)
CRICKET_SYSTEM_PROMPT="your_system_prompt"
```

## Usage 🛠️

Run the application using Poetry:

```bash
poetry run streamlit run main.py
```

The app will be available at `http://localhost:8501`.

## Deployment 🌐

The app is ready for deployment on platforms like Streamlit Cloud. Ensure you set your secrets/environment variables accordingly.

Demo URL: [cricnews-bot.streamlit.app](https://cricnews-bot.streamlit.app)
Repo URL: [Nikhil-Maheshwari-10/Cricnews-bot](https://github.com/Nikhil-Maheshwari-10/Cricnews-bot)

## License 📄
Proprietary / Private Project.
