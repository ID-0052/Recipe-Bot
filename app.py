import os
import streamlit as st
from google import genai

st.set_page_config(page_title="RecipeBot", page_icon="🍳", layout="wide")

MODEL_NAME = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 2000
TEMPERATURE = 0.2
END_MARK = "###END###"

API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": TEMPERATURE}
    )
    parts = response.candidates[0].content.parts
    text = ""
    for p in parts:
        if hasattr(p, "text"):
            text += p.text
        elif isinstance(p, dict):
            text += p.get("text", "")
    return text.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""
if "complete" not in st.session_state:
    st.session_state.complete = False

st.title("🍳 RecipeBot")

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_prompt = st.chat_input("Enter dish name or ingredients")

if user_prompt:
    recipe_prompt = f"Write a complete recipe for {user_prompt}. List ingredients with quantities then step by step instructions. End with {END_MARK}"
    reply = call_gemini(recipe_prompt)
    st.session_state.last_reply = reply
    st.session_state.complete = END_MARK in reply
    st.session_state.messages.append(("user", user_prompt))
    st.session_state.messages.append(("assistant", reply.replace(END_MARK, "")))

if not st.session_state.complete and st.session_state.last_reply != "":
    if st.button("Continue Recipe"):
        continuation = call_gemini("Continue the recipe and end with " + END_MARK)
        st.session_state.last_reply += "\n" + continuation
        st.session_state.complete = END_MARK in st.session_state.last_reply
        st.session_state.messages[-1] = ("assistant", st.session_state.last_reply.replace(END_MARK, "")))

