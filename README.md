# Deep Agents Learning App 🧠

A lightweight AI-powered learning and research assistant built using **Deep Agents, LangGraph, and Groq-powered GPT-OSS 120B**.

The application supports conversational interactions, web search, project-specific instructions, reusable skills, and conversation memory.

## Live Demo

[Try Deep Agents Learning App](https://deep-agents-learning-app-huw8qu5lygbhpwvunsnys4.streamlit.app/)

## Features

- **AI Assistant:** Powered by OpenAI's open-weight GPT-OSS 120B model through Groq.
- **Web Search:** Retrieves current information using Tavily.
- **Conversation Memory:** Maintains context using LangGraph MemorySaver.
- **Project Instructions:** Supports custom `AGENTS.md` instructions.
- **Skills Support:** Loads reusable skills from the `skills/` directory.
- **Context Management:** Uses summarization middleware to manage conversation context.
- **Streamlit UI:** Simple conversational interface.

## Tech Stack

- Python
- Streamlit
- Deep Agents
- LangGraph
- LangChain
- Groq API
- Tavily Search API
- GPT-OSS 120B


## Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/bupendra-d/Deep-Agents-Learning-App.git
cd Deep-Agents-Learning-App
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Tavily is optional. Without it, web search is disabled.

**5. Run the application**

```bash
streamlit run app.py
```

## Limitations & Notes

- **Open-Weight LLM:** This project uses OpenAI's open-weight `openai/gpt-oss-120b` model through Groq API.
- **Token Limitations:** Due to API token and usage limits, responses may be relatively short. Repeated or lengthy queries can exhaust the available token quota or rate limits.
- **Response Time:** Since the application uses the Deep Agents framework with agent execution, tool calls, and memory management, generating responses may take some time.
- **Web Search:** Requires a Tavily API key. Without it, the assistant operates without web search.

##  API Keys

- [Groq API](https://console.groq.com/keys)
- [Tavily API](https://app.tavily.com/)

## Future Improvements

This project is a work in progress. Planned improvements include:

- Additional tools and capabilities.
- Improved memory and context management.
- More reusable agent skills.
- Enhanced research and learning workflows.
- Additional Deep Agents capabilities.

---


