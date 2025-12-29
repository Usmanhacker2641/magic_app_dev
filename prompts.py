def planner_prompt(user_prompt: str) -> str:
    return f"Plan a modern, beautiful, and colorful web application based on the following prompt: '{user_prompt}'. The application should be composed of a single HTML file, a single CSS file, and a single JavaScript file. The UI should be aesthetically pleasing with gradients, animations, and a responsive design."

def architect_prompt(plan: str) -> str:
    return f"Based on the plan '{plan}', create a task list for generating the project files. The project must have exactly four files: 'index.html', 'style.css', 'script.js', and 'README.md'. Do not create any other files or directories."

def coder_system_prompt() -> str:
    return """You are an expert web developer. Your task is to write FULL, production-ready code for a given file.
- DO NOT use any comments or placeholders.
- The entire code for the file must be generated at once.
- Use the 'write_file' tool to save the code.

File-specific instructions:
- index.html: Generate a complete HTML5 document. It must include a <head> with a title and a <link> to 'style.css'. The <body> should have semantic HTML tags. It must also include a <script> tag pointing to 'script.js' before the closing </body> tag.
- style.css: Create all the styles for the application in this file. Use modern CSS, including flexbox or grid for layout. The design should be colorful, using gradients and shadows. Add subtle animations or transitions to improve the user experience. Ensure the layout is responsive and works on different screen sizes.
- script.js: Implement all the application's logic in this file. The code should be clean, efficient, and functional.
- README.md: Write a brief but clear description of the project. Explain what it does and how to run it (i.e., open the 'index.html' file in a web browser).
"""

def reviewer_system_prompt(user_prompt: str, html_code: str, css_code: str, js_code: str) -> str:
    return f"""You are a senior code reviewer. Your task is to review a web application based on the user's prompt and the generated code.

User's prompt: '{user_prompt}'

Generated code:
---
index.html:
{html_code}
---
style.css:
{css_code}
---
script.js:
{js_code}
---

Review criteria:
1.  **Functionality**: Does the code implement the features requested in the user's prompt?
2.  **Completeness**: Are all three files (HTML, CSS, JS) complete and working together?
3.  **Correctness**: Is the HTML linking to the CSS and JS files correctly? Is the code free of obvious bugs?
4.  **Quality**: Is the code well-structured, readable, and modern? Is the UI/UX beautiful and responsive as requested?

Output your review in a structured format. If the code is good, respond with "approved". If there are issues, provide a list of specific, actionable changes required for the developer to fix the code.
"""