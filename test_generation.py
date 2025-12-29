"""
Test script to verify file generation
"""
import os
from pathlib import Path

# Add agent directory to path
import sys
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from states import Plan, File
from tools import init_project_root, write_file, PROJECT_ROOT

# Initialize project directory
init_project_root()

# Create a simple test plan
test_plan = Plan(
    name="TestApp",
    description="A test application",
    techstack="html,css,javascript",
    features=["Feature 1", "Feature 2"],
    files=[
        File(path="index.html", purpose="Main HTML file"),
        File(path="style.css", purpose="Styles"),
        File(path="script.js", purpose="JavaScript logic"),
        File(path="README.md", purpose="Documentation")
    ]
)

# Test writing files
print("Testing file generation...")
print(f"Project root: {PROJECT_ROOT}")

# Create test files
test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Test Application</h1>
    <script src="script.js"></script>
</body>
</html>"""

test_css = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #333;
}"""

test_js = """console.log('Test application loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM ready');
});"""

test_readme = """# Test Application

A simple test application.

## Features
- Feature 1
- Feature 2

## Tech Stack
- HTML
- CSS
- JavaScript"""

# Write the files
print("\nWriting test files...")
results = []
results.append(write_file.run("index.html", test_html))
results.append(write_file.run("style.css", test_css))
results.append(write_file.run("script.js", test_js))
results.append(write_file.run("README.md", test_readme))

for result in results:
    print(f"  {result}")

# Verify files exist
print("\nVerifying files...")
for file in test_plan.files:
    filepath = PROJECT_ROOT / file.path
    if filepath.exists():
        print(f"  ✓ {file.path} exists ({filepath.stat().st_size} bytes)")
    else:
        print(f"  ✗ {file.path} NOT FOUND")

print("\n✅ Test complete!")
print(f"Files are in: {PROJECT_ROOT}")

