from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

class DailyBriefAgent:
    def __init__(self, calendar_tool, contacts_tool, email_tool):
        self.tools = [
            Tool(
              name="get_events",
              func=lambda d: calendar_tool.fetch_events(d),
              description="Fetch today's calendar events"
            ),
            Tool(
              name="get_birthdays",
              func=lambda d: contacts_tool.fetch_birthdays(d),
              description="Fetch today's birthdays"
            ),
            Tool(
              name="get_emails",
              func=lambda d: email_tool.fetch_unread(d),
              description="Fetch unread or important emails from Gmail"
            ),
        ]
        self.agent = initialize_agent(
            self.tools,
            OpenAI(temperature=0.2),
            agent="zero-shot-react-description",
            verbose=False
        )

    def get_brief(self, on_date):
        prompt = (
            f"Generate a friendly daily briefing for {on_date.isoformat()}.\n\n"
            "- Birthdays: use get_birthdays\n"
            "- Calendar events: use get_events\n"
            "- Unread/important emails: use get_emails\n"
            "Then summarize all findings in 3–4 sentences."
        )
        return self.agent.run(prompt)

    