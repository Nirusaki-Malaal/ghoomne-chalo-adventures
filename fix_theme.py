import os
import glob

for filename in glob.glob("templates/**/*.html", recursive=True):
    with open(filename, "r") as f:
        content = f.read()
    
    # Replace the old inverted script
    content = content.replace("""      if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.dataset.theme = 'light';
      } else {
        document.body.dataset.theme = 'dark';
      }""", """      if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.dataset.theme = 'dark';
      } else {
        document.body.dataset.theme = 'light';
      }""")
      
    content = content.replace("""      if (theme === 'light' || (!theme && window.matchMedia('(prefers-color-scheme: light)').matches)) {
        document.body.dataset.theme = 'light';
      } else {
        document.body.dataset.theme = 'dark';
      }""", """      if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.dataset.theme = 'dark';
      } else {
        document.body.dataset.theme = 'light';
      }""")

    # Also replace data-theme="dark" with data-theme="light" in <body> tags
    content = content.replace('<body data-theme="dark">', '<body data-theme="light">')

    with open(filename, "w") as f:
        f.write(content)

