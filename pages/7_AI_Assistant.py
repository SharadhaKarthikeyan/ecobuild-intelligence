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

# Initialize session state keys
if 'query_text' not in st.session_state:
    st.session_state['query_text'] = ""
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

run_query = False
active_query = ""

# Check quick query buttons
if qc1.button("🔧 Priority Retrofits", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["retrofit"]
    run_query = True
    active_query = predefined_queries["retrofit"]
if qc2.button("⚠️ Risk Case Study", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["risk"]
    run_query = True
    active_query = predefined_queries["risk"]
if qc3.button("🍃 GHG By Type", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["carbon"]
    run_query = True
    active_query = predefined_queries["carbon"]
if qc4.button("📅 Monthly Summary", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["report"]
    run_query = True
    active_query = predefined_queries["report"]
if qc5.button("💸 Cost Reduction", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["cost"]
    run_query = True
    active_query = predefined_queries["cost"]
if qc6.button("📊 Office vs School", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["compare"]
    run_query = True
    active_query = predefined_queries["compare"]
if qc7.button("💨 Aging HVACs", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["hvac"]
    run_query = True
    active_query = predefined_queries["hvac"]
if qc8.button("⌛ Historical Risks", use_container_width=True):
    st.session_state['query_text'] = predefined_queries["critical"]
    run_query = True
    active_query = predefined_queries["critical"]

st.divider()

# Text input - bind to st.session_state['query_text'] via key
st.text_input("Ask a question about the dataset:", key="query_text")

# Send Query button
if st.button("Send Query", key="send_btn"):
    run_query = True
    active_query = st.session_state['query_text']

# Process the query
if run_query and active_query:
    with st.spinner("Analyzing portfolio dataset and compiling response..."):
        response = handle_assistant_query(active_query, df)
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
