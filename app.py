import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from tavily import TavilyClient

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data
from deepagents.middleware.summarization import SummarizationMiddleware


ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

MODEL_NAME = "openai/gpt-oss-120b"
MAX_OUTPUT_TOKENS = 512
MAX_INPUT_CHARS = 3000

def get_secret(name):
    """Read a key from environment variables or Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None


SYSTEM_PROMPT = """You are a concise learning and research assistant.

- Answer directly whenever possible.
- Use tools only when necessary.
- Do not repeat the same tool call without a good reason.
- Stop searching and start answering once sufficient information is available.
- Follow AGENTS.md and relevant skills.
- Avoid unnecessary planning and delegation.
- Never claim a file was saved unless write_file succeeded.
"""


def create_model():
    api_key = get_secret("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Add GROQ_API_KEY to your .env file.")
    return ChatGroq(
        model=MODEL_NAME,
        api_key=api_key,
        max_tokens=MAX_OUTPUT_TOKENS,
        temperature=0.2,
        timeout=120,
        max_retries=2,
    )


@tool
def internet_search(query: str) -> dict:
    """Search the web for current information. Use only when needed."""
    api_key = get_secret("TAVILY_API_KEY")
    if not api_key:
        return {"error": "TAVILY_API_KEY is not configured."}

    response = TavilyClient(api_key=api_key).search(
        query=query,
        max_results=1,
        include_raw_content=False,
    )
    return {
        "query": query,
        "results": [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")[:300],
            }
            for item in response.get("results", [])
        ],
    }


def load_project_files():
    """Seed short project guidance and skill files into agent state."""
    files = {}
    agents_file = ROOT / "AGENTS.md"
    if agents_file.exists():
        files["/AGENTS.md"] = create_file_data(
            agents_file.read_text(encoding="utf-8")
        )

    skills_dir = ROOT / "skills"
    if skills_dir.exists():
        
        for path in skills_dir.rglob("SKILL.md"):
            virtual_path = "/skills/" + path.parent.relative_to(skills_dir).as_posix() + "/SKILL.md"
            
            files[virtual_path] = create_file_data(
                path.read_text(encoding="utf-8")
                )
    
        return files


def build_agent():
    model = create_model()
    tools = [internet_search] if get_secret("TAVILY_API_KEY") else []

    backend = StateBackend()
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        backend=backend,
        memory=["/AGENTS.md"],
        skills=["/skills/"],
        checkpointer=st.session_state.checkpointer,
        middleware=[
            SummarizationMiddleware(
                model=model,
                backend=backend,
                trigger=("tokens", 2000),
                keep=("tokens", 500),
            )
        ],
    )


def message_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
            if isinstance(block, str)
            or (isinstance(block, dict) and block.get("type") == "text")
        )
    return str(content)


st.set_page_config(page_title="Deep Agents Learning App", page_icon="🧠")
st.title("🧠 Deep Agents Learning App")
st.caption("Deep Agents + LangGraph + Groq GPT-OSS 120B")

if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = MemorySaver()
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []
if "seeded_thread" not in st.session_state:
    st.session_state.seeded_thread = None

with st.sidebar:
    st.subheader("Configuration")
    st.caption(f"Model: `{MODEL_NAME}`")
    st.caption(f"Thread: `{st.session_state.thread_id[:8]}`")
    st.caption("Skills: Python, AWS, LangGraph")
    if get_secret("GROQ_API_KEY"):
        st.success("Groq API key detected")
    else:
        st.error("GROQ_API_KEY is missing")
    if get_secret("TAVILY_API_KEY"):
        st.success("Tavily search enabled")
    else:
        st.info("Tavily key missing — web search disabled")

    if st.button("New conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.history = []
        st.session_state.seeded_thread = None
        st.rerun()

    if st.button("Reset app memory", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if not os.getenv("GROQ_API_KEY"):
    st.info("Create a `.env` file and add your Groq API key to start.")
    st.stop()

if "agent" not in st.session_state:
    try:
        st.session_state.agent = build_agent()
    except Exception as exc:
        st.error(f"Could not initialize the agent: {exc}")
        st.stop()

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

prompt = st.chat_input("Ask a question...")
if prompt:
    if len(prompt) > MAX_INPUT_CHARS:
        st.warning(
            f"Your message is too long ({len(prompt)} characters). "
            f"Please split it into smaller requests (limit: {MAX_INPUT_CHARS})."
        )
        st.stop()

    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"messages": [{"role": "user", "content": prompt}]}
    # Add project files once per thread; the checkpointer retains them afterward.
    if st.session_state.seeded_thread != st.session_state.thread_id:
        payload["files"] = load_project_files()
        st.session_state.seeded_thread = st.session_state.thread_id

    config = {
        "configurable": {"thread_id": st.session_state.thread_id},
        "recursion_limit": 30,
    }

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = st.session_state.agent.invoke(payload, config=config)
            messages = result.get("messages", [])
            answer = "No response was returned."
            for item in reversed(messages):
                if getattr(item, "type", "") == "ai":
                    answer = message_text(item.content)
                    if answer.strip():
                        break
            st.markdown(answer)
            st.session_state.history.append(("assistant", answer))
        except Exception as exc:
            st.error(f"Agent error: {exc}")
            st.caption(
                "If this is a rate-limit error, check your Groq TPM/RPM limits "
                "and wait before retrying."
            )
