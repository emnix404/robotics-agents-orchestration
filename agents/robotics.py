from langchain_google_genai import ChatGoogleGenerativeAI

def create_robotics_agent():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0
    )
