import re

with open('templates/admin.html', 'r') as f:
    raw_html = f.read()

# Grab header up to tabs
header = raw_html.split('<div class="admin-tabs">')[0]

# Grab just the form internally
form_content_full = raw_html.split('<form method="post" action="/admin/add" id="addPackageForm">')[1]
form_content = form_content_full.split('</form>')[0]

# Combine
html = header + '</div>\n\n  <form method="post" action="/admin/add" id="addPackageForm">' + form_content + '</form>\n  </main>\n  <script src="/statics/js/admin.js"></script>\n  <script src="/statics/js/edit.js"></script>\n</body>\n</html>'

# Change CSS link
html = html.replace("<link rel='stylesheet' type='text/css' media='screen' href='/statics/css/admin.css'>", 
                    "<link rel='stylesheet' type='text/css' media='screen' href='/statics/css/admin.css'>\n  <link rel='stylesheet' type='text/css' media='screen' href='/statics/css/edit.css'>")

# Change form action and styling wrapper
html = html.replace('action="/admin/add"', 'action="/admin/edit/{{ pkg.package_id }}"')
html = html.replace('id="addPackageForm"', 'class="edit-container" id="editPackageForm"')
html = html.replace('<h2 style="margin-bottom: 2rem; text-transform: uppercase;">Add New Package</h2>', '<div class="edit-header">\n        <h2>Edit Package: {{ pkg.title }}</h2>\n      </div>')
# Change inputs class
html = html.replace('class="admin-form-group"', 'class="edit-form-group"')

# Format the image upload field
html = html.replace('<div class="edit-form-group">\n        <label>Image Upload</label>\n        <input type="file" id="imageUpload" required accept="image/*">\n        <input type="hidden" name="card_image" id="base64Output">\n      </div>',
'''<div class="edit-form-group edit-image-preview">
        <label>Current Image</label>
        <img src="{{ pkg.card_image[1:] if pkg.card_image.startswith('./') else pkg.card_image }}" id="currentImagePreview" onerror="this.style.display='none'">
        <p style="margin-bottom:1rem;font-size:0.85rem;color:var(--text-muted);">Upload a new file to replace the current image. Base64 is generated automatically.</p>
        <input type="file" id="imageUpload" accept="image/*">
        <input type="hidden" name="card_image" id="base64Output">
      </div>''')

# Values to input fields
replacements = {
    'name="package_id" required': 'name="package_id" required value="{{ pkg.package_id }}"',
    'name="title" required': 'name="title" required value="{{ pkg.title }}"',
    'name="price" required': 'name="price" required value="{{ pkg.price }}"',
    'name="badge" required': 'name="badge" required value="{{ pkg.badge }}"',
    'name="eyebrow" required': 'name="eyebrow" required value="{{ pkg.eyebrow }}"',
    'name="facts"': 'name="facts" value="{{ pkg.facts_text }}"'
}

for k, v in replacements.items():
    html = html.replace(k, v)

# Update Textareas
html = re.sub(r'<textarea name="summary"([^>]*)></textarea>', r'<textarea name="summary"\1>{{ pkg.summary }}</textarea>', html, flags=re.DOTALL)
html = re.sub(r'<textarea name="itinerary"([^>]*)></textarea>', r'<textarea name="itinerary"\1>{{ pkg.itinerary_text }}</textarea>', html, flags=re.DOTALL)
html = re.sub(r'<textarea name="inclusions"([^>]*)></textarea>', r'<textarea name="inclusions"\1>{{ pkg.inclusions_text }}</textarea>', html, flags=re.DOTALL)
html = re.sub(r'<textarea name="exclusions"([^>]*)></textarea>', r'<textarea name="exclusions"\1>{{ pkg.exclusions_text }}</textarea>', html, flags=re.DOTALL)
html = re.sub(r'<textarea name="carry"([^>]*)></textarea>', r'<textarea name="carry"\1>{{ pkg.carry_text }}</textarea>', html, flags=re.DOTALL)
html = re.sub(r'<textarea name="highlights"([^>]*)></textarea>', r'<textarea name="highlights"\1>{{ pkg.highlights_text }}</textarea>', html, flags=re.DOTALL)

# Update Buttons
html = html.replace('<button type="submit" class="admin-btn">Add Package</button>', 
                    '<div class="edit-actions">\n        <a href="/admin" class="btn-cancel">Cancel</a>\n        <button type="submit" class="btn-update">Update Package</button>\n      </div>')

with open('templates/edit_package.html', 'w') as f:
    f.write(html)
