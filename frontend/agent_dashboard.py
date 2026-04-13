import streamlit as st
import requests
import os

# This way it defaults to localhost for dev but uses the Render URL in production.
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Agent Dashboard")
st.caption("Review pending customer requests")

# Fetch pending reviews
try:
    response = requests.get(f"{API_URL}/pending", timeout=120)
    response.raise_for_status()
    pending = response.json()["pending"]
except Exception as e:
    st.error(f"Could not connect to the API. ({e})")
    st.stop()

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

            edited = st.text_area(
                "Edit response (optional)",
                key=f"edit_{thread_id}",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Approve", key=f"approve_{thread_id}", type="primary"):
                    try:
                        payload = {"thread_id": thread_id, "approved": "yes"}
                        if edited.strip():
                            payload["edited_response"] = edited
                        requests.post(f"{API_URL}/review", json=payload, timeout=120)
                        st.success("Approved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to approve. ({e})")

            with col2:
                if st.button("Reject", key=f"reject_{thread_id}"):
                    try:
                        requests.post(f"{API_URL}/review", json={
                            "thread_id": thread_id,
                            "approved": "no",
                        }, timeout=120)
                        st.warning("Rejected")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to reject. ({e})")

# All threads section
st.divider()
st.subheader("All Threads")

if "selected_thread" not in st.session_state:
    st.session_state.selected_thread = None

try:
    threads_response = requests.get(f"{API_URL}/threads", timeout=120)
    threads_response.raise_for_status()
    threads = threads_response.json()["threads"]

    for thread in threads:
        status_emoji = {"active": "🟢", "pending_review": "🟡"}.get(thread["status"], "⚪")
        if st.button(
            f"{status_emoji} {thread['thread_id']} — {thread['status']}",
            key=f"thread_{thread['thread_id']}",
        ):
            st.session_state.selected_thread = thread["thread_id"]
except Exception as e:
    st.error(f"Could not load threads. ({e})")

# Show conversation history for selected thread
if st.session_state.selected_thread:
    st.divider()
    st.subheader(f"Conversation: {st.session_state.selected_thread}")

    try:
        state_response = requests.get(
            f"{API_URL}/thread/{st.session_state.selected_thread}/state",
            timeout=120,
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

    try:
        msg_response = requests.get(
            f"{API_URL}/thread/{st.session_state.selected_thread}/messages",
            timeout=120,
        )
        msg_response.raise_for_status()
        messages = msg_response.json()["messages"]

        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    except Exception as e:
        st.error(f"Could not load messages. ({e})")