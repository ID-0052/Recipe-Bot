import os
import streamlit as st
from google import genai

st.set_page_config(page_title="RecipeBot", page_icon="🍳", layout="wide")

MODEL_NAME = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 2000
TEMPERATURE = 0.2

API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": TEMPERATURE}
    )
    candidate = response.candidates[0]
    parts = candidate.content.parts
    text = ""
    for p in parts:
        if hasattr(p, "text"):
            text += p.text
        elif isinstance(p, dict):
            text += p.get("text", "")
    return text.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

col1, col2 = st.columns([8, 1])
col1.title("🍳 RecipeBot")

if col2.button("New Chat"):
    st.session_state.messages = []
    st.session_state.last_reply = ""
    st.session_state.last_prompt = ""
    st.rerun()

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_prompt = st.chat_input("Enter dish name or ingredients")

if user_prompt:
    st.session_state.messages.append(("user", user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    recipe_prompt = f"Write a complete recipe for {user_prompt}. List ingredients with quantities then step by step instructions."

    with st.chat_message("assistant"):
        reply = call_gemini(recipe_prompt)
        st.session_state.last_reply = reply
        st.session_state.last_prompt = recipe_prompt
        st.markdown(reply)

    st.session_state.messages.append(("assistant", reply))

if st.session_state.last_reply:
    if st.button("Continue Recipe"):
        continuation = call_gemini("Continue this recipe:\n" + st.session_state.last_reply)
        st.session_state.last_reply += "\n" + continuation
        st.session_state.messages[-1] = ("assistant", st.session_state.last_reply)
        st.rerun()

