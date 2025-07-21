import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# SCOPES needed for Calendar, Contacts, Gmail
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]

class GoogleCalendarTool:
    @staticmethod
    def oauth_flow():
        flow = Flow.from_client_secrets_file(
            "client_secrets.json",
            scopes=SCOPES,
            redirect_uri="http://localhost:8501"
        )
        auth_url, _ = flow.authorization_url(access_type="offline")
        st.write(f"[Click to authorize]({auth_url})")
        code = st.experimental_get_query_params().get("code")
        if code:
            flow.fetch_token(code=code[0])
            return flow.credentials
        st.stop()

    def __init__(self, creds: Credentials):
        self.cal = build("calendar", "v3", credentials=creds)

    def fetch_events(self, query_date: datetime.date):
        iso = query_date.isoformat()
        events = self.cal.events().list(
            calendarId="primary",
            timeMin=f"{iso}T00:00:00Z",
            timeMax=f"{iso}T23:59:59Z",
        ).execute().get("items", [])
        return [e.get("summary", "No title") for e in events]


class ContactsTool:
    def __init__(self, creds: Credentials):
        self.people = build("people", "v1", credentials=creds)

    def fetch_birthdays(self, query_date: datetime.date):
        conns = self.people.people().connections().list(
            resourceName="people/me",
            personFields="names,birthdays"
        ).execute().get("connections", [])
        today = (query_date.month, query_date.day)
        names = []
        for p in conns:
            for b in p.get("birthdays", []):
                d = b["date"]
                if (d.get("month"), d.get("day")) == today:
                    names.append(p["names"][0]["displayName"])
                    break
        return names


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
