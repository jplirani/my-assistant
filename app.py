import streamlit as st
from datetime import date
from agent_tools import GoogleCalendarTool, ContactsTool, EmailTool
from agents import DailyBriefAgent
import os

# Setup page config
st.set_page_config("📅 Morning Brief", layout="centered", initial_sidebar_state="collapsed")
st.title("☀️ Your Personal Morning Brief")

# ─── Load OpenAI key ───────────────────────────────────────────────────────────
OPENAI_KEY = st.secrets.get("openai", {}).get("key")
if not OPENAI_KEY:
    st.error("🔑 Missing OpenAI key! Add it under Manage app → Secrets.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

# Initialize session state
if "creds" not in st.session_state:
    st.session_state.creds = None
if "brief_generated" not in st.session_state:
    st.session_state.brief_generated = False
if "show_brief" not in st.session_state:
    st.session_state.show_brief = False

# ─── Connection Status Panel ───────────────────────────────────────────────────
def connection_status():
    if st.session_state.creds:
        st.success("✅ Connected to Google services")
        return True
    return False

# ─── Main App Flow ─────────────────────────────────────────────────────────────
def main():
    # Step 1: Google Connection
    st.header("1. Connect to Google")
    if not connection_status():
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Connect Google Account", key="connect_btn", type="primary"):
                st.session_state.connecting = True
        
        if st.session_state.get("connecting"):
            creds = GoogleCalendarTool.oauth_flow()
            if creds:
                st.session_state.creds = creds
                st.session_state.connecting = False
                st.rerun()
    else:
        st.divider()
    
    # Step 2: Generate Brief (only show if connected)
    if connection_status():
        st.header("2. Generate Your Brief")
        if not st.session_state.brief_generated:
            if st.button("Generate Today's Brief", type="primary", key="generate_btn"):
                with st.spinner("🔍 Gathering your daily information..."):
                    try:
                        # Setup tools
                        cal_tool = GoogleCalendarTool(st.session_state.creds)
                        contact_tool = ContactsTool(st.session_state.creds)
                        email_tool = EmailTool(st.session_state.creds)
                        
                        # Run agent
                        agent = DailyBriefAgent(
                            calendar_tool=cal_tool,
                            contacts_tool=contact_tool,
                            email_tool=email_tool
                        )
                        st.session_state.summary = agent.get_brief(on_date=date.today())
                        st.session_state.brief_generated = True
                        st.session_state.show_brief = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating brief: {str(e)}")
        else:
            st.success("Brief generated successfully!")
            st.divider()
    
    # Step 3: Display Brief
    if st.session_state.get("show_brief"):
        st.header("3. Your Morning Brief")
        st.markdown(st.session_state.summary)
        
        if st.button("Generate New Brief", key="new_brief_btn"):
            st.session_state.brief_generated = False
            st.session_state.show_brief = False
            st.rerun()

# ─── Sidebar (minimal) ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    if st.button("Disconnect Google", type="secondary"):
        st.session_state.creds = None
        st.session_state.brief_generated = False
        st.session_state.show_brief = False
        st.success("Disconnected from Google services")
        st.rerun()
    
    st.divider()
    st.caption("App Version: 1.0")
    st.caption("Need help? Contact support@example.com")

# Run the app
if __name__ == "__main__":
    main()