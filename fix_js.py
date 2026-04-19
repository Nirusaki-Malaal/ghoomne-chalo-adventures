import glob

# For JS files, we want to replace 
# window.matchMedia('(prefers-color-scheme: light)').matches
# with window.matchMedia('(prefers-color-scheme: dark)').matches
# and update defaultTheme logical assignment.

for filename in glob.glob("statics/js/*.js"):
    with open(filename, "r") as f:
        content = f.read()

    # In admin.js and packages.js
    content = content.replace("const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;", "const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;")
    content = content.replace('const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;', 'const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;')
    
    content = content.replace("const defaultTheme = storedTheme || (prefersLight ? 'light' : 'dark');", "const defaultTheme = storedTheme || (prefersDark ? 'dark' : 'light');")
    content = content.replace('const defaultTheme = storedTheme || (prefersLight ? "light" : "dark");', 'const defaultTheme = storedTheme || (prefersDark ? "dark" : "light");')
    
    # In script.js
    content = content.replace('applyTheme(storedTheme || "dark", { skipStorage: true });', 'applyTheme(storedTheme || "light", { skipStorage: true });')

    with open(filename, "w") as f:
        f.write(content)

