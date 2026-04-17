import re
import os

filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics', 'js', 'script.js')

with open(filepath, 'r') as f:
    content = f.read()

# Replace the giant constant object with an initialized 'let' and the fetch call.
new_content = re.sub(
    r'const PACKAGE_DETAILS = \{.*?\n\};\n',
    r'let PACKAGE_DETAILS = {};\n\n'
    r'async function fetchPackages() {\n'
    r'  try {\n'
    r'    const res = await fetch("/api/packages");\n'
    r'    if (res.ok) {\n'
    r'      PACKAGE_DETAILS = await res.json();\n'
    r'    }\n'
    r'  } catch (error) {\n'
    r'    console.error("Failed to fetch packages", error);\n'
    r'  }\n'
    r'}\n\n'
    r'// Call immediately to preload packages\n'
    r'fetchPackages();\n',
    content,
    flags=re.DOTALL
)

with open(filepath, 'w') as f:
    f.write(new_content)
