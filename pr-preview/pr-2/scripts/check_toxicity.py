import json
import os
import sys

from bs4 import BeautifulSoup
from groq import Groq


client = Groq()

def text_is_toxic(text) -> bool:
    """Analyze toxicity of text using Groq"""
    print(text[:4096])
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "system",
                "content": "Determine whether or not the given string contains any offensive material. Respond with true if the following string contains any offensive material and false if it contains no offensive material.\nRespond in json format with a field \"reason\" set to an explanation and \"flag\" set to true or false."
            },
            {
                "role": "user",
                "content": f"'''\n{text[:4096]}\n'''" #  Limit to ~1024 tokens
            }
        ],
        temperature=0,
        max_completion_tokens=128, # Limit to ~512 characters
        response_format={"type": "json_object"},
    )
    result = completion.choices[0].message.content
    print("Model response:", result)
    return json.loads(result)["flag"]

def file_is_toxic(file_path: str) -> bool:
    """Read file and analyze its file path and content for toxicity"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        file_content = file.read()
        if file_path.endswith(".html"):
            file_content = BeautifulSoup(file_content, "html.parser").get_text()
        if text_is_toxic(file_path):
            print(f"❌ Toxic content detected in file path of {file_path}")
            return True
        elif text_is_toxic(file_content):
            print(f"❌ Toxic content detected in file content of {file_path}")
            return True
        else:
            print(f"✅ No toxic content found in file path or content of {file_path}")
            return False

if __name__ == "__main__":
    offensive_found = False
    for file in os.popen("git diff --name-only HEAD^ HEAD").read().split(): # For each file in the diff,
        if os.path.exists(file) and file_is_toxic(file): # Check it if it exists and is toxic
            offensive_found = True
    sys.exit(1) if offensive_found else sys.exit(0) # Exit with a non-zero status code if toxic