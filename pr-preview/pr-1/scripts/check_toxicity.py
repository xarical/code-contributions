import os
import sys

from bs4 import BeautifulSoup
from detoxify import Detoxify


def toxicity(text) -> bool:
    """Analyze toxicity of text using detoxify"""
    result = Detoxify('multilingual').predict(text[:2048]) # Limit to ~512 tokens (model constraint)
    return result["toxicity"] > 0.7

def check_file_content(file_path: str) -> bool:
    """Read file and analyze its file path and content for toxicity"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        file_content = file.read()
        if file_path.endswith(".html"):
            file_content = BeautifulSoup(file_content, "html.parser").get_text()
        if toxicity(file_path):
            print(f"❌ Toxicity detected in file path of {file_path}")
            return True
        elif toxicity(file_content):
            print(f"❌ Toxicity detected in file content of {file_path}")
            return True
        else:
            return False

if __name__ == "__main__":
    modified_files = os.popen("git diff --name-only HEAD^ HEAD").read().split()
    offensive_found = False
    for file in modified_files:
        if os.path.exists(file) and check_file_content(file):
            offensive_found = True
    if offensive_found:
        sys.exit(1)
    else:
        print("✅ No offensive content found.")
        sys.exit(0)