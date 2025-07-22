import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.markdown("""
<h2 style='text-align: center; margin-bottom: 1rem;'>
🚀 WebTestGPT &nbsp; | &nbsp; <span style='font-size:2rem;'>Your Testing Copilot</span>
</h2>
""", unsafe_allow_html=True)

col1, col_sep, col2 = st.columns([4, 0.3, 4])

st.markdown("""
<style>
.code-block { background:#23232e; color:#dcdcdc; padding:1rem; border-radius:12px;
    font-family:'Fira Mono','Consolas',monospace; font-size:15px; min-height:270px; 
    max-height:300px; overflow-y:auto; white-space:pre-wrap;
    border:1px solid rgba(255,255,255,0.10); box-shadow:0 2px 12px rgba(90,255,255,0.09);}
[data-testid="stChatInput"] { margin-top:7px !important; padding-top:0 !important;}
</style>
""", unsafe_allow_html=True)

components.html(
    """
    <script>
    function callFlush() {
      navigator.sendBeacon("https://your-flask-service.onrender.com/flush");
    }
    window.addEventListener('unload', callFlush);
    window.addEventListener('beforeunload', callFlush);
    </script>
    """, height=0
)

with col1:
    st.header("🧪 Test your website")
    url = st.text_input("🔗 Enter Website URL", placeholder="e.g. https://example.com")
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        generate_button = st.button("⚡ Generate Test Script", use_container_width=True)
    with btn_col2:
        run_button = st.button("▶️ Run Test Script", use_container_width=True)
    status_container = st.empty()
    def set_status(text="..."):
        if text:
            icon = "✅" if "success" in text.lower() or "generated!" in text.lower() or "complete" in text.lower() else (
                   "🔴" if "error" in text.lower() else "💡")
            html = f"<div style='height:24px; margin-bottom:8px; font-weight:bold; color:#00b4d8; font-size:1.08em;'>{icon} {text}</div>"
            status_container.markdown(html, unsafe_allow_html=True)
        else:
            status_container.empty()
    set_status()
    output_container = st.empty()
    if "output_content" not in st.session_state:
        st.session_state["output_content"] = "⏳ Waiting for output..."
    def render_output(text, mode="auto"):
        if mode == "code":
            cleaned = text.replace("```python", "").replace("```", "")
            output_container.code(cleaned, language="python")
        else:
            html = f"""
            <div class="code-block" id="outputbox">{text}</div>
            <script>
                const outputBox = window.parent.document.getElementById("outputbox");
                if(outputBox){{
                    outputBox.scrollTop = outputBox.scrollHeight;
                }}
            </script>
            """
            output_container.markdown(html, unsafe_allow_html=True)
    render_output(st.session_state["output_content"], mode="auto")
    if generate_button:
        st.session_state["output_content"] = ""
        set_status("⚡ Generating test script...")
        try:
            with requests.post(
                "https://webtestgpt.onrender.com/generate_script",
                json={"url": url},
                stream=True,
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        decoded = chunk.decode("utf-8")
                        st.session_state["output_content"] += decoded
                        render_output(st.session_state["output_content"], mode="code")
            set_status("✅ Generated!")
        except Exception as e:
            st.session_state["output_content"] = f"❌ Error: {e}"
            render_output(st.session_state["output_content"], mode="auto")
            set_status("❌ Error during generation.")
    if run_button:
        st.session_state["output_content"] = "⏳ Analyzing your website..."
        render_output(st.session_state["output_content"], mode="auto")
        set_status("🔄 Running test script...")
        try:
            with requests.get(
                "https://webtestgpt.onrender.com/run_test",
                stream=True,
            ) as response:
                response.raise_for_status()
                run_log = ""
                st.session_state["output_content"] = ""
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        decoded = chunk.decode("utf-8")
                        st.session_state["output_content"] += decoded
                        render_output(st.session_state["output_content"], mode="auto")
            set_status("🟢 Run complete.")
        except Exception as e:
            st.session_state["output_content"] = f"❌ Error: {e}"
            render_output(st.session_state["output_content"], mode="auto")
            set_status("❌ Error during run.")

with col2:
    st.markdown("<h3 style='margin-bottom: 10px;'>🤖 Chatbot Assistant</h3>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.markdown("""
    <style>
    .chat-box { height:350px; overflow-y:auto; border:1px solid #555;
      border-radius:10px; padding:12px; background:#0f0f0f;
      font-family:'Fira Mono','Consolas',monospace; color:#fff;
      white-space:pre-wrap; scroll-behavior:smooth; display:flex; flex-direction:column; }
    .message { margin-bottom:12px; padding:10px 14px; border-radius:12px; max-width:80%; word-break:break-word; }
    .user-msg { background:#005f73; color:#e0f7fa; align-self:flex-end; margin-left:auto;}
    .bot-msg { background:#0a9396; color:#e0f7fa; align-self:flex-start; margin-right:auto;}
    .spinner { border:4px solid rgba(255,255,255,0.2); border-top:4px solid #00b4d8; border-radius:50%; width:20px; height:20px; animation:spin 1s linear infinite; margin-left:10px; display:inline-block; vertical-align:middle;}
    @keyframes spin {0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
    </style>
    """, unsafe_allow_html=True)
    chat_container = st.empty()
    def render_chat(show_spinner=False):
        html = "<div class='chat-box' id='chatbox'>"
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "bot-msg"
            emoji = "🧑" if msg["role"] == "user" else "🤖"
            html += f"<div class='message {cls}'><b>{emoji}</b> {msg['content']}</div>"
        if show_spinner:
            html += "<div class='bot-msg'><b>🤖</b> <span class='spinner'></span> <span style='opacity:0.6'>Thinking…</span></div>"
        html += "</div>"
        chat_container.markdown(html, unsafe_allow_html=True)
        components.html("""
            <script>
                const chatBox = parent.document.getElementById('chatbox');
                if (chatBox) { chatBox.scrollTop = chatBox.scrollHeight; }
            </script>
        """, height=0)
    render_chat()
    user_input = st.chat_input("Type your message here… 💬")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": ""})
        render_chat(show_spinner=True)
        bot_response = ""
        try:
            with requests.post("https://webtestgpt.onrender.com/chat", json={"user": user_input}, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        decoded = chunk.decode("utf-8")
                        bot_response += decoded
                        st.session_state.messages[-1]["content"] = bot_response
                        render_chat(show_spinner=True)
            render_chat(show_spinner=False)
        except Exception as e:
            st.session_state.messages[-1]["content"] = f"❌ Error: {e}"
            render_chat(show_spinner=False)