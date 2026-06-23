import streamlit as st
import pandas as pd
from src.ai_reports import handle_assistant_query

# Verify session state
if 'df' not in st.session_state:
    st.switch_page("app.py")

df = st.session_state['df']

st.title("🤖 EcoBuild Assistant")
st.write("Ask natural language questions about your property portfolio's energy consumption, retrofit candidates, risk profiles, or carbon footprint.")

# Predefined question buttons in grid layout
st.markdown("### 💡 Quick Queries")
qc1, qc2, qc3, qc4 = st.columns(4)
qc5, qc6, qc7, qc8 = st.columns(4)

predefined_queries = {
    "retrofit": "Which buildings should be retrofitted first?",
    "risk": "Why is a selected building high risk?",
    "carbon": "Which building type has the highest carbon emissions?",
    "report": "Generate a monthly energy performance report.",
    "cost": "What are the top 5 actions to reduce cost?",
    "compare": "Compare office buildings and school buildings.",
    "hvac": "Which buildings have old HVAC systems?",
    "critical": "Show critical-risk buildings built before 1990."
}

query_to_run = ""

with qc1:
    if st.button("🔧 Priority Retrofits", use_container_width=True):
        query_to_run = predefined_queries["retrofit"]
with qc2:
    if st.button("⚠️ Risk Case Study", use_container_width=True):
        query_to_run = predefined_queries["risk"]
with qc3:
    if st.button("🍃 GHG By Type", use_container_width=True):
        query_to_run = predefined_queries["carbon"]
with qc4:
    if st.button("📅 Monthly Summary", use_container_width=True):
        query_to_run = predefined_queries["report"]
with qc5:
    if st.button("💸 Cost Reduction", use_container_width=True):
        query_to_run = predefined_queries["cost"]
with qc6:
    if st.button("📊 Office vs School", use_container_width=True):
        query_to_run = predefined_queries["compare"]
with qc7:
    if st.button("💨 Aging HVACs", use_container_width=True):
        query_to_run = predefined_queries["hvac"]
with qc8:
    if st.button("⌛ Historical Risks", use_container_width=True):
        query_to_run = predefined_queries["critical"]

st.divider()

# Input box
user_input = st.text_input("Ask a question about the dataset:", value=query_to_run if query_to_run else "", placeholder="e.g. Which buildings should be retrofitted first?")

# Chat history initialization
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if st.button("Send Query", key="send_btn") or (query_to_run and not user_input):
    active_query = user_input if user_input else query_to_run
    if active_query:
        with st.spinner("Analyzing portfolio dataset and compiling response..."):
            response = handle_assistant_query(active_query, df)
            # Append to history
            st.session_state['chat_history'].append((active_query, response))

# Display Chat History (most recent first)
if st.session_state['chat_history']:
    st.markdown("### 💬 Conversation")
    for q, r in reversed(st.session_state['chat_history']):
        st.markdown(f"**👤 You**: {q}")
        st.markdown(f"**🤖 EcoBuild AI**: {r}")
        st.markdown("---")
else:
    st.info("Select a Quick Query button or write in the chat bar to query the database.")
