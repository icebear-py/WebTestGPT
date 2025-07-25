from flask import Flask,request,jsonify,Response,stream_with_context
from llm_agent_claude import generate_test_script
from playwright_runner import extract_dom
from run_test import run_test_script
from interpret_log import interpret_log
from flush_memory import flush_memory
from chat_agent import chat_with_llm
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/',methods=['GET','POST'])
def index():
    return {'message':'Hello master'}


@app.route('/generate_script',methods=['POST'])
def generate_script():
    try:
        data = request.json
        url = data['url']
        if not url:
            return {'error':'URL is required'},400
        dom_info = extract_dom(url)
        if dom_info['isError']==1:
            return {'error':dom_info['error']},400
        test_script = generate_test_script(dom_info)
        return Response(
            stream_with_context(test_script),
            mimetype='text/plain'
        )
    except Exception as e:
        print(e)
        return {'error':str(e)},500


@app.route('/run_test', methods=['GET'])
def run_test():
    try:
        resp = run_test_script()
        print('running test')
        if isinstance(resp, dict) and resp.get('error'):
            return {'error': resp['error']}

        if not os.path.exists("results/result_log.txt"):
            with open('results/result_log.txt') as f:
                log_details = f.read()
            return {'error': 'Error in reading the log.', 'log': log_details}, 500

        return Response(
            stream_with_context(interpret_log()),
            content_type='text/plain'
        )

    except Exception as e:
        return {'error': str(e)}


@app.route('/chat',methods=['POST'])
def chat():
    data = request.json
    userip = data['user']
    if not userip:
        return {'error':'User input required'},400

    response = chat_with_llm(userip)
    if isinstance(response, dict) and response['error']:
        return {'error':response['error']},500

    return Response(
        stream_with_context(chat_with_llm(userip)),
        content_type='text/plain'
    )

@app.route('/flush', methods=['POST','GET'])
def flush():
    try:
        flush_memory()
        return jsonify({'status': 'flushed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 204

if __name__ == '__main__':
    app.run(debug=True)
