## 🚀 TestGPT – The AI Testing Copilot for SaaS applications
**TestGPT is an advanced AI-driven platform for automated SaaS web application testing. Engineered with a Python Flask backend and a modern Streamlit dashboard, it integrates enterprise-grade LLMs (Claude) to dynamically analyze any web application's DOM and generate high-fidelity Playwright test scripts on demand.
After test script generation, TestGPT executes these scripts on the server and provides comprehensive, structured feedback about which website functionalities are operating as intended and which are failing or require attention.**

<i>Note : Deployed site may take time to load for the first time since flask app is deployed on free deploying service (Render).</i>

## ✨ Features
- **Automated Test Generation:** Paste any website URL—TestGPT extracts the DOM, formulates prompts, and uses a large language model to synthesize and stream Playwright E2E tests dynamically.
- **Script Execution & Analysis:** All generated tests run server-side. The system parses results and automatically produces a human-readable and machine-parseable report, detailing which user flows/specific features pass or fail and why.
- **Interactive AI Chatbot:** Engage with an assistant capable of answering questions about your website's detected issues, Playwright/test code, and debugging strategies. The chatbot can recommend specific code changes, architectural fixes, or explain probable root causes, all grounded in the actual observed test results.
- **Real-Time Streaming:** The user interface instantly streams test code as it's generated and provides live output/logs as tests execute, making the workflow transparent and interactive.
- **Cloud/CI Ready:** The architecture is stateless, fully containerizable, and cloud-deployable, ideal for integration into continuous integration pipelines or as a standalone SaaS product.
- **Built-in chat assistant:**  Get stepwise explanations, debugging help, and usage guidance from an AI chatbot.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Python)
- **Backend:** Flask (Python)
- **Testing Engine:** Playwright (Python)  
- **AI Model:** Claude via DeepInfra API  
- **Real-time communication:** Streaming generators (Flask, Streamlit)
- **Deployment Ready for:** Render, Railway, Docker, or your own cloud

---

## 🚦 How it Works

1. **Paste Any Website URL**  
   The user provides a URL in the Streamlit dashboard.

2. **DOM Extraction & LLM Call**  
   Backend fetches and parses the DOM, sends context + prompt to the LLM.

3. **On-the-fly Script Generation**  
   LLM streams out Playwright Python code, line by line, into the Streamlit UI.

4. **Run the Test**  
   Generated code is executed with Playwright; results and logs are streamed back to the UI.

5. **Chatbot for Help**  
   Users can chat with an integrated AI assistant for real-time help and explanations.

---

## 🚀 Getting Started

**1. Clone the repo:**
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

**2. Set up your Python environment:**
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install   # Download browser bins for Playwright
```

**3. Set your environment variables:**
- Add your DeepInfra Claude API key and any required Flask/Streamlit secrets in a `.env` file or using environment variables.

**4. Run the backend (Flask):**
```bash
python app.py
```
*(or via Gunicorn for production, e.g., `gunicorn app:app --timeout 120`)*

**5. In a new terminal, run the frontend (Streamlit):**
```bash
streamlit run streamlit_ui.py
```

_Note: For cloud (Render/Railway), see the deployment section below._

---

## 🌐 Deployment

- **Render/Railway:**  
  Provision two services: one for Flask, one for Streamlit UI.  
  *(Set `python -m playwright install` as a start script for both. See `/requirements.txt` for dependencies.)*

- **Docker:**  
  Use your own Docker Compose with two containers: one for Flask API, one for Streamlit.

---

## 💡 Usage Tips

- "Generate Test Script" streams code in real time—wait for the process to complete!
- "Run Test Script" shows logs and errors as they happen; scroll to view big outputs.
- Use the chatbot for usage help, debugging, or to ask about generated code.

---

## ⚠️ Security & .env

- **Never commit your `.env` or API keys:**  
  Always use `.gitignore` to keep these private.
- Set secrets via environment variables in production.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Contributors

- Ansh
  
