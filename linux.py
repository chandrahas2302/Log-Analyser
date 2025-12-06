import requests
import json

def  send_to_ollama(log_text):

    prompt = f"""
    Analyse the following RAW Linux system logs and provide the summary of overall health status, critical errors, hardware issues, resource problems, and security alerts. 
    Categorize the findings.
{log_text}
"""

     
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "tinyllama", "prompt": prompt, "stream": False}
    )

    return response.json().get("response", "No output returned")


LOG_FILE = r"datasets\linux_logs.txt"

def main():
    with open(LOG_FILE, "r", errors="ignore") as f:
        log_text = f.read()

    output = send_to_ollama(log_text)
    print(output)

    with open("output_linux.json","w",encoding="utf-8") as json_file:
      json.dump({"analysis": output}, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
