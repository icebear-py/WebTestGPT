import json
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def load_conversations(convo_path='memory/conversation.json') -> list:
    if os.path.exists(convo_path):
        with open(convo_path,'r') as f:
            return json.load(f)
    else:
        return []


def save_conversations(conversation_history: list,convo_path='memory/conversation.json') -> None:
    with open(convo_path,'w') as f:
        json.dump(conversation_history,f,indent=2)


def chat_with_llm(input: str):
    user_input = """You are an expert QA analyst chatbot named WebTestGPT who understands the issues in the website code(html,css,js),
    and recommend the corrections user can make according to the result logs and interpreted output (use conversation history)
    Answer in clear, concise, and actionable format.Try minimizing output tokens and respond fast
    Only include necessary code examples if asked specifically or if solution involves changes.
    Do not add extra empty lines , keep the response as minimal as possible.
    Use the full context of conversation for continuity.\n\n """
    user_input += f"User:{input}"
    openai = OpenAI(
        api_key=f"{OPENAI_API_KEY}",
        base_url="https://api.deepinfra.com/v1/openai"
    )

    conversation_history = load_conversations()
    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = openai.chat.completions.create(
            model="anthropic/claude-4-sonnet",
            messages=conversation_history,
            stream = True
        )
        full_response = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
                full_response+=content
        conversation_history.append({"role": "assistant", "content": full_response})
        save_conversations(conversation_history)
    except Exception as e:
        return {'error':e}

if __name__ == "__main__":
    print(chat_with_llm('How can i add error handling in my code?'))
