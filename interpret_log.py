import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OpenAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_llm(system_prompt: str, user_prompt: str, conversation_history: list):
    openai = OpenAI(
        api_key=f"{OpenAI_API_KEY}",
        base_url="https://api.deepinfra.com/v1/openai",
    )
    conversation_history.append({"role": "system", "content": system_prompt})
    conversation_history.append({"role": "user", "content": user_prompt})
    try:
        stream = openai.chat.completions.create(
            model="anthropic/claude-4-sonnet",
            messages=conversation_history,
            stream=True
        )
        full_reply = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
                full_reply += content
        conversation_history.append({"role": "assistant", "content": full_reply})
        save_conversations(conversation_history)
    except Exception as e:
        yield f"# Error: {str(e)}"


def build_prompt(log_content: str) -> list:
    system_prompt = """
You are an expert software tester. A Playwright test script was generated and executed on a webpage. Below is the test log output.
From the given log, generate a coder understandable response. Do not add extra empty lines , keep the response as minimal as possible, test the functionality of input url from result log
maximum 2 line space Use this structure:
  "Small description of website , what it does , how is its performance , how many elements are working or failing, how is the structure , etc." 
  "<element_name_or_identifier> followed with a ✅ or ❌ symbol (working/not working)
  "<brief explanation of what this element does and whether it's functioning (one line max)>",
  "solution" (only if not working): 
    "fix" "<how to fix the code>",
    "correct_code" "<updated code snippet>" in a code block
    
Be flexible — element names, class names, and IDs may differ. Generalize issues if exact matches are missing, but maintain precision when suggesting fixes. 
Avoid repetition and unnecessary tokens. Keep the response concise but complete. Use conversation history to infer the element names and identity and the purpose of webapp. 
"""

    user_prompt = "#Log:" + log_content

    return [system_prompt,user_prompt]


def load_conversations(convo_path='memory/conversation.json') -> list:
    if os.path.exists(convo_path):
        with open(convo_path,'r') as f:
            return json.load(f)
    else: return []


def save_conversations(conversation_history: list,convo_path='memory/conversation.json') -> None:
    with open(convo_path,'w') as f:
        json.dump(conversation_history,f,indent=2)


def interpret_log(log_path = "results/result_log.txt"):
    if not os.path.exists(log_path):
        print(f"Log file not found at: {log_path}")
        return None

    with open(log_path, 'r') as f:
        log_content = f.read()
    system_prompt,user_prompt = build_prompt(log_content)
    conversation_history = load_conversations()
    for chunk in call_llm(system_prompt,user_prompt,conversation_history):
        yield chunk

if __name__ == "__main__":
    print(interpret_log())




