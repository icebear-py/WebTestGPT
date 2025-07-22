import os
files_to_delete = ['memory/conversation.json','results/result_log.txt','test_scripts/test_script.py']
def flush_memory():
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            pass
    return {'flushed':True}

if __name__ == "__main__":
    flush_memory()