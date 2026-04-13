import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
# so that it defaults to localhost for dev but uses the Render URL in production

st.title("Agent Dashboard")
st.caption("Review pending customer requests")

# Fetch pending reviews
response = requests.get(f"{API_URL}/pending")
pending = response.json()["pending"]

if not pending:
    st.info("No pending reviews. All clear!")
else:
    for item in pending:
        thread_id = item["thread_id"]
        info = item["interrupt_info"]

        with st.expander(f"Thread: {thread_id}", expanded=True):
            st.subheader("Customer Message")
            st.write(info["customer_message"])

            st.subheader("Proposed Action")
            st.markdown(info["proposed_action"])

            # Editable response field
            edited = st.text_area(
                "Edit response (optional)",
                key=f"edit_{thread_id}",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Approve", key=f"approve_{thread_id}", type="primary"):
                    payload = {"thread_id": thread_id, "approved": "yes"}
                    if edited.strip():
                        payload["edited_response"] = edited
                    requests.post(f"{API_URL}/review", json=payload)
                    st.success("Approved!")
                    st.rerun()

            with col2:
                if st.button("Reject", key=f"reject_{thread_id}"):
                    requests.post(f"{API_URL}/review", json={
                        "thread_id": thread_id,
                        "approved": "no",
                    })
                    st.warning("Rejected")
                    st.rerun()

# Show all threads
st.divider()
st.subheader("All Threads")

threads_response = requests.get(f"{API_URL}/threads")
threads = threads_response.json()["threads"]

if "selected_thread" not in st.session_state:
    st.session_state.selected_thread = None

for thread in threads:
    status_emoji = {"active": "🟢", "pending_review": "🟡"}.get(thread["status"], "⚪")
    if st.button(
        f"{status_emoji} {thread['thread_id']} — {thread['status']}",
        key=f"thread_{thread['thread_id']}",
    ):
        st.session_state.selected_thread = thread["thread_id"]

# Show conversation history for selected thread
if st.session_state.selected_thread:
    st.divider()
    st.subheader(f"Conversation: {st.session_state.selected_thread}")

    # Check for escalation summary
    try:
        state_response = requests.get(
            f"{API_URL}/thread/{st.session_state.selected_thread}/state"
        )
        if state_response.ok:
            state_data = state_response.json()
            if state_data.get("escalation_summary"):
                st.error("🚨 Escalated Thread")
                st.info(f"**Agent Summary:** {state_data['escalation_summary']}")
            if state_data.get("escalation_reason"):
                st.caption(f"Reason: {state_data['escalation_reason']}")
    except Exception:
        pass

    # Show messages
    msg_response = requests.get(
        f"{API_URL}/thread/{st.session_state.selected_thread}/messages"
    )
    messages = msg_response.json()["messages"]

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
