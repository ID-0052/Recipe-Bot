import os
import streamlit as st
from google import genai

st.set_page_config(page_title="RecipeBot", page_icon="🍳", layout="wide")

MODEL_NAME = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 1500
TEMPERATURE = 0.2

API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def call_gemini(prompt):
    r = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": TEMPERATURE}
    )
    t = ""
    for p in r.candidates[0].content.parts:
        if hasattr(p,"text"):
            t += p.text
        elif isinstance(p,dict):
            t += p.get("text","")
    return t.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "reply" not in st.session_state:
    st.session_state.reply = ""
if "awaiting_more" not in st.session_state:
    st.session_state.awaiting_more = False

st.title("🍳 RecipeBot")

for r,c in st.session_state.messages:
    with st.chat_message(r):
        st.markdown(c)

q = st.chat_input("Enter dish name")

if q:
    prompt = f"Write a complete recipe for {q}. Ingredients then steps."
    out = call_gemini(prompt)
    st.session_state.reply = out
    st.session_state.awaiting_more = len(out) > 1300
    st.session_state.messages.append(("user", q))
    st.session_state.messages.append(("assistant", out))

if st.session_state.awaiting_more:
    if st.button("Continue Recipe"):
        more_prompt = "Continue this recipe exactly from where it stopped:\n\n" + st.session_state.reply[-4000:]
        more = call_gemini(more_prompt)
        st.session_state.reply += "\n" + more
        st.session_state.messages[-1] = ("assistant", st.session_state.reply)
        if len(more) < 500:
            st.session_state.awaiting_more = False
