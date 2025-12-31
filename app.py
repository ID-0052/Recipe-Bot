import os
import streamlit as st
from google import genai

st.set_page_config(page_title="RecipeBot", page_icon="🍳", layout="wide")

MODEL_NAME = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 1800
TEMPERATURE = 0.2
END_MARK = "###END###"

API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt):
    r = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": TEMPERATURE}
    )
    text = ""
    for p in r.candidates[0].content.parts:
        if hasattr(p, "text"):
            text += p.text
        elif isinstance(p, dict):
            text += p.get("text","")
    return text.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "reply" not in st.session_state:
    st.session_state.reply = ""
if "complete" not in st.session_state:
    st.session_state.complete = True

st.title("🍳 RecipeBot")

for r,c in st.session_state.messages:
    with st.chat_message(r):
        st.markdown(c)

q = st.chat_input("Enter dish")

if q:
    prompt = f"Write a complete recipe for {q}. Ingredients then steps. End with {END_MARK}"
    out = call_gemini(prompt)
    st.session_state.reply = out
    st.session_state.complete = END_MARK in out
    st.session_state.messages.append(("user", q))
    st.session_state.messages.append(("assistant", out.replace(END_MARK,"")))

if st.session_state.reply and not st.session_state.complete:
    if st.button("Continue Recipe"):
        more = call_gemini("Continue the recipe and end with " + END_MARK)
        st.session_state.reply += "\n" + more
        st.session_state.complete = END_MARK in st.session_state.reply
        st.session_state.messages[-1] = ("assistant", st.session_state.reply.replace(END_MARK,""))

