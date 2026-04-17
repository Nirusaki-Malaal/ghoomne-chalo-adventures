import os
filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'admin.html')
with open(filepath, 'r') as f:
    html = f.read()

js_replacement = """
  <script>
    const imageUpload = document.getElementById('imageUpload');
    const base64Output = document.getElementById('base64Output');
    const form = document.getElementById('addPackageForm');

    if (imageUpload) {
      imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = function(evt) {
            const img = new Image();
            img.onload = function() {
              const canvas = document.createElement('canvas');
              const MAX_WIDTH = 800;
              const MAX_HEIGHT = 800;
              let width = img.width;
              let height = img.height;

              if (width > height) {
                if (width > MAX_WIDTH) {
                  height = Math.round((height * MAX_WIDTH) / width);
                  width = MAX_WIDTH;
                }
              } else {
                if (height > MAX_HEIGHT) {
                  width = Math.round((width * MAX_HEIGHT) / height);
                  height = MAX_HEIGHT;
                }
              }
              canvas.width = width;
              canvas.height = height;
              const ctx = canvas.getContext('2d');
              ctx.drawImage(img, 0, 0, width, height);
              base64Output.value = canvas.toDataURL(file.type, 0.8);
            };
            img.src = evt.target.result;
          };
          reader.readAsDataURL(file);
        }
      });
    }

    if (form) {
      form.addEventListener('submit', function(e) {
        if (imageUpload && imageUpload.files.length > 0 && !base64Output.value) {
          e.preventDefault();
          alert('Processing image... please wait a second and try again.');
        }
      });
    }
  </script>
"""
import re
html = re.sub(r'<script>\s*const imageUpload.*?</script>', js_replacement, html, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(html)
