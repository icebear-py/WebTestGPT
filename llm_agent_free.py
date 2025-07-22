import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENROUTER_API_KEY')
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def clean_code_response(response: str) -> str:
    if response.startswith("```python"):
        response = response[len("```python"):].strip()
    if response.endswith("```"):
        response = response[:-3].strip()
    return response

def build_prompt(dom: dict) -> list:
    url = dom.get("url", "")
    title = dom.get("title", "")
    elements = dom.get("elements", [])

    system_prompt = f"""
        You are an expert QA engineer and contextual test automation developer.
        You are testing a web application hosted at: {url}
        The page title is: "{title}" , and the elements of the webpage will be provided to you.
        Generate a well-structured Playwright Python test script that simulates a real user interacting with the website.
        ### Tasks:
        1. Understand the website's purpose from its title, URL, and elements.
           - If it's a utility webapp, try entering information and check if it works correctly according to context of webapp.
           - If it's a form or survey, fill and submit it and check its response on submitting.
           - If it's an e-commerce page, click product cards, "Add to Cart" buttons, etc.
        2. Do NOT assume fixed class names, IDs, or selectors. Instead:
           - Detect visible elements likely showing data (e.g., temperature in weather app, time in timer app,errors) by checking text or tags.
           - Use common patterns like numeric values, icons, or status messages.
           - Prefer broader selectors or JS evaluation over hardcoded ones like.
           - Check for empty or invalid inputs but do not use hardcoded check, instead search the whole page to 
             detect if website provides error mssg for invalid inputs like No matching location in weather app.
           - Ensure your test is adaptive, verifying functionality regardless of HTML/CSS structure.
           - The testing should not be stopped even if any of functionality is not working, use asyncio if required
        3. Interact with all relevant elements: inputs, buttons, selects, text areas and log their working or issues.
        4. Assert:
           - Inputs accept text
           - Buttons trigger UI updates
           - Content changes or loads correctly after interactions
        5. Wait properly for elements to appear using Playwright best practices.
        6. Log every interaction.
        ###Logging Requirement
        While writing the test, log every interaction into a Python list called `test_log`, like:
        # After interacting with an element
        for ex - The test log should save the element , its response(to check further if it was right or wrong) , its status(working or not) , issue (if not working), selector(where issue occurs), but remember to add important infromation which maybe used to asnwer further questions
        Your log should include enough detail to later answer user questions or explain issues. Include short code snippets if relevant. Make the test generic — for example, weather data may appear in any part of the page, not under a fixed class.
        Also save the log in the folder ../results/result_log.txt with all the necessary info about website like the instance of code where error occurs or what logic is wrong to later answer user questions
        ### Your Output:
        Please return a full working Python script using Playwright. Use `page.fill()`, `page.click()`, and `page.wait_for_selector()` as needed. Include at least 3–5 meaningful assertions based on what the app seems to do. Replace page.url() with page.url only thats wrong syntax, Only add UTF-8 chars in the code
        Your code should look like a realistic end-to-end test, not just a demo and the code should check each functionality and save a log in the format that the log can be further interpreted by LLM for solving those issues or explaining a problem, also print the log in the end. Return the code only and no other explanation, if something is necessary then keep it as python comment.
    """

    user_prompt = "### Elements Detected on the Page:"
    for i, el in enumerate(elements, 1):
        tag = el.get('tag')
        type_ = el.get('type')
        name = el.get('name')
        text = el.get('text')
        placeholder = el.get('placeholder')
        user_prompt += f"- [{tag}] name: {name}, type: {type_}, text: {text}, placeholder: {placeholder}\n"


    return [system_prompt.strip(),user_prompt.strip()]

def call_llm(system_prompt: str,user_prompt) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen-2.5-coder-32b-instruct:free",
        "messages": [{"role": "system", "content":f"{system_prompt}"},
            {"role": "user", "content":f"{user_prompt}"}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data).json()
        print(response)
        reply = response['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return f"# Error: {str(e)}"

def generate_test_script(dom:dict):
    prompt = build_prompt(dom)
    resp = call_llm(prompt[0],prompt[1])
    with open("test_scripts/test_script.py", "w") as f:
        f.write(clean_code_response(resp))
    print(resp)
    return clean_code_response(resp)

dom_new = {'isError': 0, 'url': 'https://snehaweatherapp.netlify.app/', 'title': 'weather app', 'elements': [{'tag': 'input', 'type': 'text', 'name': None, 'placeholder': 'enter city name', 'text': '', 'selector': '<input type="text" id="cityInput" placeholder="enter city name">'}, {'tag': 'button', 'type': None, 'name': None, 'placeholder': None, 'text': 'GET WEATHER', 'selector': '<button id="searchbtn"> GET WEATHER </button>'}]}

if __name__ == "__main__":
    generate_test_script(dom_new)
