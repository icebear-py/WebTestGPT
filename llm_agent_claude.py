import requests,json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OpenAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
        Generate a well-structured headless Playwright Python test script that simulates a real user interacting with the website headlessly.
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
           - The testing should not be stopped even if any of functionality is not working, use asyncio if required.
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
        Also save the log in the folder results/result_log.txt(result dir already exists) with all the necessary info about website like the instance of code where error occurs or what logic is wrong to later answer user questions
        ### Your Output:
        Please return a full working python test script using Playwright. Use `page.fill()`, `page.click()`, and `page.wait_for_selector()` as needed. Include at least 3–5 meaningful assertions based on what the app seems to do. Replace page.url() with page.url only thats wrong syntax,
        Your code should look like a realistic end-to-end detailed test, not just a demo and the code should check each functionality and save a minimal log in the format that the log can be further interpreted by LLM for solving those issues or explaining a problem, also print the log in the end.
        The test script aims to check all the functionalities on the current page only, if the page redirects it should come back and log Redirect to -> and should not test the redirected page.Test only the inputted url. End testing when all the functionalities of url are tested.
        If special characters like degree(°) are required, add # -- coding: utf-8-- in starting and do required encoding handling if log also contain some special symbols. Program/log file should not have UnicodeDecodeError 
        The log file should not be unnecessarily empty and big ,Log total no. of elements, working , nonworking , warning etc in start and log details of each element in single line and add maximum info in less lines because the whole log is to be interpreted later.
        Test script should not be small and should check each and every functionality and log it, return the code only and no other explanation and no comments and no extra spaces or empty lines. 
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

def call_llm(system_prompt: str, user_prompt: str):
    from openai import OpenAI
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
        collected = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                if content != 'DONE':
                    collected += content
                    yield content
        conversation_history.append({"role": "assistant", "content": collected})
        os.makedirs("memory", exist_ok=True)
        with open("memory/conversation.json", "w") as f:
            json.dump(conversation_history, f, indent=2)
    except Exception as e:
        yield f"# Error: {str(e)}"



conversation_history = []
def generate_test_script(dom: dict):
    prompt = build_prompt(dom)
    test_script = ""
    os.makedirs("test_scripts", exist_ok=True)
    with open("test_scripts/test_script.py", "w", encoding="utf-8") as f:
        for chunk in call_llm(prompt[0], prompt[1]):
            test_script += str(chunk)
            yield chunk
        f.write(clean_code_response(test_script))

dom_demo = {'isError': 0, 'url': 'https://demo.automationtesting.in/', 'title': 'Index', 'elements': [{'tag': 'button', 'type': 'button', 'name': None, 'placeholder': None, 'text': 'Sign In', 'selector': '<button id="btn1" type="button" class="btn btn-primary-outline" style="background-color:#0177b5">Sign In</button>'}, {'tag': 'button', 'type': 'button', 'name': None, 'placeholder': None, 'text': 'Skip Sign In', 'selector': '<button id="btn2" type="button" class="btn btn-primary-outline" style=" background-color: #0177b5 ;">Skip Sign In</button>'}, {'tag': 'input', 'type': 'text', 'name': None, 'placeholder': 'Email id for Sign Up', 'text': '', 'selector': '<input id="email" type="text" placeholder="Email id for Sign Up" ng-model="emailid" autofocus="">'}]}
dom_ansh = {'isError': 0, 'url': 'https://anshweather.netlify.app/', 'title': 'Weather api', 'elements': [{'tag': 'input', 'type': 'search', 'name': None, 'placeholder': 'Enter city name', 'text': '', 'selector': '<input type="search" placeholder="Enter city name" class="py-1 pl-2 rounded-3xl font-bold bg-white/10 md:text-xl text-white" id="searchinput">'}]}

if __name__ == "__main__":
    generate_test_script(dom_demo)
