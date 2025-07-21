import streamlit as st
from datetime import date
from agent_tools import GoogleCalendarTool, ContactsTool, EmailTool
from agents import DailyBriefAgent
import os

st.set_page_config("📅 Morning Brief", layout="centered")
# ─── Load your OpenAI key from Streamlit secrets ───────────────────────────────
OPENAI_KEY = st.secrets["openai"]["key"]
if not OPENAI_KEY:
    st.sidebar.error("Missing OpenAI key! Add it under Manage app → Secrets.")
    st.stop()

# Make it available to LangChain / OpenAI libraries
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

st.title("☀️ Your Personal Morning Brief")

# ─── Sidebar: Connection ──────────────────────────────────────────────────────

st.sidebar.header("🔗 Google Connection")

# Kick off OAuth when the user clicks “Connect Google”
if st.sidebar.button("Connect Google"):
    creds = GoogleCalendarTool.oauth_flow()
    if creds:
        st.session_state.creds = creds

# If we don’t yet have credentials, run oauth_flow (which will render
# the “Authorize with Google” link and then halt via st.stop())
if "creds" not in st.session_state:
    # This will either show the consent link or an error and then stop
    GoogleCalendarTool.oauth_flow()
    st.stop()

# ─── Main: Generate the Brief ─────────────────────────────────────────────────

if st.button("Get Today's Brief"):
    creds = st.session_state.creds

    # Instantiate each tool with the same Google credentials
    cal_tool     = GoogleCalendarTool(creds)
    contact_tool = ContactsTool(creds)
    email_tool   = EmailTool(creds)

    # Build and run the agent
    agent = DailyBriefAgent(
        calendar_tool=cal_tool,
        contacts_tool=contact_tool,
        email_tool=email_tool
    )
    summary = agent.get_brief(on_date=date.today())

    # Display the result
    st.markdown("### Your Morning Brief")
    st.markdown(summary)