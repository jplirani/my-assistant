import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]

class GoogleCalendarTool:
    def __init__(self, creds: Credentials):
        self.service = build("calendar", "v3", credentials=creds)
    
    # Add your calendar-related methods here
    def fetch_events(self, date):
        # Implement your calendar event fetching logic
        pass

    @staticmethod
    def oauth_flow():
        # Keep your existing oauth_flow implementation
        redirect_uri = st.secrets["google"]["redirect_uri"]
        
        flow = Flow.from_client_secrets_file(
            "client_secrets.json",
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )

        if "google_creds" in st.session_state:
            return Credentials.from_authorized_user_info(st.session_state.google_creds)

        query_params = st.query_params.to_dict()
        if "code" in query_params:
            try:
                flow.fetch_token(code=query_params["code"])
                creds = flow.credentials
                st.session_state.google_creds = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                st.query_params.clear()
                st.rerun()
                return None
            except Exception as e:
                st.session_state.pop("google_creds", None)
                st.query_params.clear()
                st.rerun()
                return None

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        st.write("Please authorize")
        st.markdown(f"[Authorize]({auth_url})")
        st.stop()
        return None

class ContactsTool:
    def __init__(self, creds: Credentials):
        self.people = build("people", "v1", credentials=creds)

    def fetch_birthdays(self, query_date: datetime.date):
        try:
            # Ensure query_date is a date object
            if not isinstance(query_date, datetime.date):
                raise ValueError("query_date must be a datetime.date object")
                
            # Get connections with birthdays
            conns = self.people.people().connections().list(
                resourceName="people/me",
                personFields="names,birthdays",
                pageSize=1000  # Increase if you have more contacts
            ).execute().get("connections", [])
            
            # Prepare today's date tuple
            today = (query_date.month, query_date.day)
            names = []
            
            for person in conns:
                # Skip if no birthdays
                if 'birthdays' not in person:
                    continue
                    
                for birthday in person.get('birthdays', []):
                    if 'date' not in birthday:
                        continue
                        
                    date_info = birthday['date']
                    # Check if month and day match (ignore year)
                    if (date_info.get('month'), date_info.get('day')) == today:
                        if 'names' in person and len(person['names']) > 0:
                            names.append(person['names'][0].get('displayName', 'Unknown'))
                        break
            return names
            
        except Exception as e:
            st.error(f"Error fetching birthdays: {str(e)}")
            return []  # Return empty list on error


class EmailTool:
    def __init__(self, creds: Credentials):
        self.gmail = build("gmail", "v1", credentials=creds)

    def fetch_unread(self, query_date: datetime.date):
        # Fetch messages labeled UNREAD
        results = self.gmail.users().messages().list(
            userId="me", labelIds=["UNREAD"], maxResults=10
        ).execute().get("messages", [])
        summaries = []
        for m in results:
            msg = self.gmail.users().messages().get(
                userId="me", id=m["id"], format="metadata", metadataHeaders=["Subject","From"]
            ).execute()
            hdrs = {h["name"]:h["value"] for h in msg["payload"]["headers"]}
            summaries.append(f"{hdrs.get('Subject','<no subject>')} from {hdrs.get('From','')}")
        return summaries
