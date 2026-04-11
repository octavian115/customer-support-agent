import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000"

st.title("TaskFlow Support")
st.caption("Hi! How can I help you today?")

# Generate a unique thread ID per session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Show user message
    st.session_state.messages.append({"role": "human", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)

    # Send to API
    response = requests.post(f"{API_URL}/chat", json={
        "thread_id": st.session_state.thread_id,
        "message": prompt,
    })
    data = response.json()

    # Show agent response
    agent_message = data["response"]
    st.session_state.messages.append({"role": "ai", "content": agent_message})
    with st.chat_message("ai"):
        st.markdown(agent_message)