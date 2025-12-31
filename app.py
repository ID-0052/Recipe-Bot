import os
import streamlit as st
from google import genai

st.set_page_config(
    page_title="RecipeBot",
    page_icon="🍳",
    layout="wide"
)

MODEL_NAME = "gemini-2.5-flash"
MAX_TOKENS = 5000

API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("Missing GEMINI_API_KEY in environment or Streamlit secrets.")
    st.stop()

def call_gemini(prompt: str) -> str:
    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"max_output_tokens": MAX_TOKENS}
    )

    try:
        return response.candidates[0].content.parts[0].text.strip()
    except Exception:
        return "Sorry, I couldn't generate a recipe."

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

for i, (title, chat) in enumerate(st.session_state.history):
    if st.sidebar.button(title, key=f"history_{i}"):
        st.session_state.messages = chat.copy()
        st.rerun()

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_prompt = st.chat_input("Enter dish name or ingredients")

if user_prompt:
    st.session_state.messages.append(("user", user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    recipe_prompt = (
        f"Write complete recipe for {user_prompt}, "
        "Include all ingredients with quantities and simple instructions"
        "No greetings, tips, or extra commentary, but no turnications."
    )

    with st.chat_message("assistant"):
        with st.spinner("Searching recipe..."):
            reply = call_gemini(recipe_prompt)
            st.markdown(reply)

    st.session_state.messages.append(("assistant", reply))

    title = user_prompt[:40]
    st.session_state.history.append(
        (title, st.session_state.messages.copy())
    )
