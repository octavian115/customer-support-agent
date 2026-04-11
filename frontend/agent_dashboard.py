import streamlit as st
import requests

API_URL = "http://localhost:8000"

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

for thread in threads:
    status_emoji = {"active": "🟢", "pending_review": "🟡"}.get(thread["status"], "⚪")
    st.write(f"{status_emoji} **{thread['thread_id']}** — {thread['status']}")
