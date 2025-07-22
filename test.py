from flask import Flask, Response
import time

app = Flask(__name__)


@app.route('/stream')
def stream():
    def generate():
        yield "Starting the stream...\n"
        for i in range(1, 6):
            time.sleep(1)
            yield f"Chunk {i}...\n"
        yield "Stream finished.\n"

    return Response(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
