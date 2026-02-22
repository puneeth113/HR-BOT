import streamlit as st
from pymongo import MongoClient
from openai import OpenAI

st.set_page_config(page_title="Chatbot", layout="wide")

st.title("Mitra.ai")

# ==========================
# Sidebar Configuration
# ==========================
st.sidebar.header("Configuration")

# MongoDB
mongo_uri = st.sidebar.text_input("MongoDB URI", type="password")

if st.sidebar.button("Connect MongoDB"):
    try:
        client = MongoClient(mongo_uri)
        db = client["chat_database"]
        collection = db["chat_history"]
        st.session_state.chat_collection = collection
        st.sidebar.success("MongoDB Connected")
    except Exception as e:
        st.sidebar.error(f"MongoDB Error: {e}")

# OpenRouter API Key
openrouter_key = st.sidebar.text_input("OpenRouter API Key", type="password")

# Model selection
model = st.sidebar.selectbox(
    "Select Model",
    [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku",
        "meta-llama/llama-3-8b-instruct"
    ]
)

if st.sidebar.button("Save OpenRouter Key"):
    try:
        client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        st.session_state.openai_client = client
        st.session_state.selected_model = model
        st.sidebar.success("OpenRouter Connected")
    except Exception as e:
        st.sidebar.error(f"API Error: {e}")

# ==========================
# Chat Section
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    if "openai_client" not in st.session_state:
        st.error("Please configure OpenRouter API in sidebar first.")
    else:
        client = st.session_state.openai_client
        model = st.session_state.selected_model

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.write(user_input)

        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages
        )

        ai_reply = response.choices[0].message.content

        st.session_state.messages.append(
            {"role": "assistant", "content": ai_reply}
        )

        with st.chat_message("assistant"):
            st.write(ai_reply)

        # Save to MongoDB if connected
        if "chat_collection" in st.session_state:
            st.session_state.chat_collection.insert_one({
                "conversation": st.session_state.messages,
                "model": model
            })