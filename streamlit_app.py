import streamlit as st

customer_page = st.Page("frontend/customer_chat.py", title="Customer Chat", icon="💬")
dashboard_page = st.Page("frontend/agent_dashboard.py", title="Agent Dashboard", icon="📋")

pg = st.navigation([customer_page, dashboard_page])
pg.run()