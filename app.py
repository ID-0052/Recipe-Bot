import os
import streamlit as st
from google import genai
import logging

st.set_page_config(page_title="RecipeBot", page_icon="🍳", layout="wide")

# Model/config
MODEL_NAME = "gemini-2.5-flash"
# Set a sensible max (adjust if you know model supports more)
MAX_OUTPUT_TOKENS = 1500
TEMPERATURE = 0.2

# API key
API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("Missing GEMINI_API_KEY in environment or Streamlit secrets.")
    st.stop()

# Create client once
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "temperature": TEMPERATURE
            }
        )
        # Debug: log whole response for troubleshooting
        logging.debug("Gemini raw response: %s", response)

        # Safely extract and join all parts
        candidate = response.candidates[0]
        parts = getattr(candidate.content, "parts", None) or candidate.content.get("parts", [])
        content_texts = []
        for p in parts:
            # depending on shape, `p` may be an object with .text or a dict
            text = getattr(p, "text", None)
            if text is None and isinstance(p, dict):
                text = p.get("text", "")
            if text:
                content_texts.append(text)
        # fallback: sometimes there's top-level `text` on candidate
        if not content_texts:
            text_fallback = getattr(candidate.content, "text", None) or candidate.content.get("text", "")
            content_texts.append(text_fallback or "")

        reply = "".join(content_texts).strip()
        return reply or "Sorry, I couldn't generate a recipe."

    except Exception as e:
        logging.exception("Error calling Gemini")
        return f"Sorry, I couldn't generate a recipe. (Error: {e})"

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([8, 1])
col1.title("🍳 RecipeBot")

if col2.button("New Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.title("Chat History")
# limit history display to last N items
MAX_HISTORY_ITEMS = 50
for i, (title, chat) in enumerate(st.session_state.history[-MAX_HISTORY_ITEMS:]):
    if st.sidebar.button(title, key=f"history_{i}"):
        st.session_state.messages = chat.copy()
        st.rerun()

# render previous messages
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_prompt = st.chat_input("Enter dish name or ingredients")

if user_prompt:
    st.session_state.messages.append(("user", user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # clearer prompt, avoid typos; explicit structure request
    recipe_prompt = (
    f"Write a complete recipe for {user_prompt}. "
    "List ingredients with quantities, then give clear step-by-step instructions. "
    "No greetings or extra text."
    )

    with st.chat_message("assistant"):
        with st.spinner("Searching recipe..."):
            reply = call_gemini(recipe_prompt)
            st.markdown(reply)

    st.session_state.messages.append(("assistant", reply))

    title = user_prompt[:40]
    st.session_state.history.append((title, st.session_state.messages.copy()))
    # keep history bounded
    if len(st.session_state.history) > 200:
        st.session_state.history = st.session_state.history[-200:]
