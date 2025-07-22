# -*- coding: utf-8 -*-
import subprocess

def run_test_script(script_path="test_scripts/test_script.py"):
    try:
        result = subprocess.run(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False

        )
        output = result.stdout
        return output

    except Exception as e:
        return {'error':e}

if __name__ == "__main__":
    print(run_test_script())
