from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    github_username = "Enriquedlrm16"

    def fetch_github_profile(self, username):
        url = f"https://api.github.com/users/{username}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "career-chatbot"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return {}
            return resp.json()
        except requests.RequestException:
            return {}
    def fetch_github_repos(self, username):
        url = f"https://api.github.com/users/{username}/repos"
        params = {"per_page": 100, "sort": "updated"}
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "career-chatbot"}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code != 200:
                return []
            return resp.json()
        except requests.RequestException:
            return []
        
    def format_github_info(self, profile, repos, max_repos=5):
        lines = []
        if profile:
            name = profile.get("name") or profile.get("login")
            bio = profile.get("bio")
            location = profile.get("location")
            company = profile.get("company")
            blog = profile.get("blog")
            public_repos = profile.get("public_repos")
            followers = profile.get("followers")
            following = profile.get("following")
            lines.append(f"GitHub profile for {name} (@{profile.get('login')}):")
            if bio:
                lines.append(f"Bio: {bio}")
            if location:
                lines.append(f"Location: {location}")
            if company:
                lines.append(f"Company: {company}")
            if blog:
                lines.append(f"Website: {blog}")
            if public_repos is not None:
                lines.append(f"Public repos: {public_repos}")
            if followers is not None and following is not None:
                lines.append(f"Followers: {followers}, Following: {following}")
        if repos:
            def stars(r):
                return r.get("stargazers_count", 0) or 0
            top = sorted(repos, key=stars, reverse=True)[:max_repos]
            if top:
                lines.append("Top repositories by stars:")
                for r in top:
                    name = r.get("name")
                    desc = r.get("description") or "No description"
                    lang = r.get("language") or "Unknown language"
                    url = r.get("html_url")
                    lines.append(f"- {name} ({lang}) - {desc}. URL: {url}")
        return "\n".join(lines).strip()
    
    def __init__(self):
        self.openai = OpenAI()
        self.name = "Enrique de la Rosa"
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
        self.github_username = "Enriquedlrm16"
        profile = self.fetch_github_profile(self.github_username)
        repos = self.fetch_github_repos(self.github_username)
        self.github_info = self.format_github_info(profile, repos)
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## GitHub:\n{self.github_info}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()

    title = "💼 Professional AI Assistant"
    description = (
        "Ask me about my education, professional background, skills, "
        "projects, and experience."
    )

    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="gray",
        radius_size="lg",
        font=[gr.themes.GoogleFont("Inter")]
    )

    with gr.Blocks(theme=theme, fill_height=True, css="""
        .gradio-container {max-width: 900px; margin: auto;}
        footer {visibility: hidden;}
    """) as demo:

        gr.Markdown(
            f"""
            # {title}
            {description}
            """
        )

        gr.ChatInterface(
        me.chat,
        type="messages",
        chatbot=gr.Chatbot(
            show_copy_button=True, 
            avatar_images=(None, "https://media.licdn.com/dms/image/sync/v2/D4D27AQG7Rb0p9zUaBw/articleshare-shrink_800/articleshare-shrink_800/0/1711701976469?e=2147483647&v=beta&t=i5HLLwak-8ss9t_WM9h3ytIHgPyAVEiguZyI5ieKgMs")
        ),
        textbox=gr.Textbox(
            placeholder="Type your question here… (e.g., What technologies do you work with?)",
            show_label=False
        ),
        submit_btn="Send",  
        examples=[
            "What is your professional background?",
            "What technologies do you specialize in?",
            "Tell me about your latest projects",
            "How can I contact you?"
        ],
        )

    demo.launch()
    