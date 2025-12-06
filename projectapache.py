import requests
import json

def send_to_ollama(log_text):
    prompt = (
       "Analyse the following Apache/Ngnix logs and provide the summary of overall health status, critical errors, pod/container issues, resource problems, and network/connectivity errors.:"
        "Categorize the findings."
        f"{log_text}"
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "tinyllama", "prompt": prompt, "stream": False}
    )

    return response.json().get("response", "No output returned")


LOG_FILE = r"datasets\sample_apache_ngnix_logs.txt"

def main():
    with open(LOG_FILE, "r", errors="ignore") as f:
        log_text = f.read()

    output = send_to_ollama(log_text)
    print(output)

    with open("output.json","w",encoding="utf-8") as json_file:
      json.dump({"analysis": output}, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()


import json
import subprocess

user_prompt = input("Enter your prompt")

with open("output.json","r") as f:
    json_data = f.read()

full_prompt = user_prompt+"\n\nHere is the data:\n"+json_data

result=subprocess.run(
    ["ollama","run","tinyllama"],
    input=full_prompt,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True
)

print(result.stdout)