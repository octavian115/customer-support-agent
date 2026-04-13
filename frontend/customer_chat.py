import streamlit as st
import requests
import time
import random

API_URL = "http://localhost:8000"

st.title("TaskFlow Support")
st.caption("Hi! How can I help you today?")

if st.sidebar.button("New Conversation"):
    st.session_state.thread_id = f"chat-{random.randint(1000, 9999)}"
    st.session_state.messages = []
    st.session_state.pending = False
    st.rerun()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"chat-{random.randint(1000, 9999)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending" not in st.session_state:
    st.session_state.pending = False

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# If waiting for review, poll for updates
if st.session_state.pending:
    st.info("⏳ Let me check with my team on this. I'll get back to you shortly.")

    response = requests.get(
        f"{API_URL}/thread/{st.session_state.thread_id}/messages"
    )
    api_messages = response.json()["messages"]

    if len(api_messages) > len(st.session_state.messages):
        for msg in api_messages[len(st.session_state.messages):]:
            st.session_state.messages.append(msg)
        st.session_state.pending = False
        st.rerun()
    else:
        time.sleep(3)
        st.rerun()

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "human", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)

    # Call API with a status message (not inside chat_message)
    with st.spinner("Thinking..."):
        response = requests.post(f"{API_URL}/chat", json={
            "thread_id": st.session_state.thread_id,
            "message": prompt,
        })
        data = response.json()

    if data["status"] == "pending_review":
        st.session_state.pending = True
        st.rerun()
    else:
        agent_message = data["response"]
        st.session_state.messages.append({"role": "ai", "content": agent_message})
        with st.chat_message("ai"):
            st.markdown(agent_message)