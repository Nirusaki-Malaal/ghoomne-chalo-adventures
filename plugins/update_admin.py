import re
import os
filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'admin.html')
with open(filepath, 'r') as f:
    html = f.read()

new_form = """    <form method="post" action="/admin/add" style="margin-bottom: 3rem; background: rgba(128,128,128,0.1); padding: 2rem; border-radius: 8px; border: 1px solid var(--border);" id="addPackageForm">
      <h2 style="margin-bottom: 2rem; text-transform: uppercase;">Add New Package</h2>
      
      <div class="admin-form-group">
        <label>ID</label>
        <input type="text" name="package_id" required placeholder="e.g., andaman_nicobar">
      </div>
      <div class="admin-form-group">
        <label>Title</label>
        <input type="text" name="title" required placeholder="Andaman Nicobar">
      </div>
      <div class="admin-form-group">
        <label>Price</label>
        <input type="text" name="price" required placeholder="e.g., ₹14999">
      </div>
      <div class="admin-form-group">
        <label>Badge</label>
        <input type="text" name="badge" required placeholder="e.g., Popular">
      </div>
      <div class="admin-form-group">
        <label>Eyebrow</label>
        <input type="text" name="eyebrow" required placeholder="Tropical Island">
      </div>
      <div class="admin-form-group">
        <label>Image Upload</label>
        <input type="file" id="imageUpload" required accept="image/*">
        <input type="hidden" name="card_image" id="base64Output">
      </div>
      <div class="admin-form-group">
        <label>Summary</label>
        <textarea name="summary" rows="3" required placeholder="A beautiful tropical island..."></textarea>
      </div>
      
      <!-- New detailed fields -->
      <div class="admin-form-group">
        <label>Itinerary (Day-wise Plan)</label>
        <textarea name="itinerary" rows="6" placeholder="Day 1: Arrival
- Check into hotel
- Rest
Day 2: Sightseeing
- Visit museum
- Boat ride"></textarea>
        <small style="opacity:0.7">Format: 'Day X: Title' on one line, followed by bullet points starting with '-'</small>
      </div>
      <div class="admin-form-group">
        <label>Inclusions (One per line)</label>
        <textarea name="inclusions" rows="3" placeholder="- 3 Nights Stay
- All Meals"></textarea>
      </div>
      <div class="admin-form-group">
        <label>Exclusions (One per line)</label>
        <textarea name="exclusions" rows="3" placeholder="- Flights
- Personal Expenses"></textarea>
      </div>
      <div class="admin-form-group">
        <label>Things To Carry (One per line)</label>
        <textarea name="carry" rows="3" placeholder="- Sunglasses
- Light Jacket"></textarea>
      </div>
      <div class="admin-form-group">
        <label>Highlights (One per line)</label>
        <textarea name="highlights" rows="3" placeholder="- Beach walk
- Local cuisine"></textarea>
      </div>
      <div class="admin-form-group">
        <label>Tags/Facts (Comma separated)</label>
        <input type="text" name="facts" placeholder="e.g. 5 Days, Adventure, Family">
      </div>

      <button type="submit" class="admin-btn">Add Package</button>
    </form>"""

html = re.sub(r'<form method="post".*?</form>', new_form, html, flags=re.DOTALL)

# Fix the table showing the existing packages
new_table = """      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Image</th>
            <th>Summary</th>
            <th style="min-width: 150px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          {% for pkg in packages %}
          <tr>
            <td>{{ pkg.package_id }}</td>
            <td>{{ pkg.title }}</td>
            <td>
                {% if pkg.card_image %}
                  <img src="{{ pkg.card_image[1:] if pkg.card_image.startswith('./') else pkg.card_image }}" alt="Image" style="max-width: 50px; border-radius: 4px;" onerror="this.style.display='none'">
                {% else %}
                  No Image
                {% endif %}
            </td>
            <td>{{ pkg.summary[:50] }}...</td>
            <td>
              <div style="display: flex; gap: 0.5rem; justify-content: flex-start;">
                <a href="/admin/edit/{{ pkg.package_id }}" class="admin-btn" style="padding: 0.5rem 0.8rem; text-decoration: none; font-size: 0.9rem;">Edit</a>
                <form method="post" action="/admin/delete/{{ pkg.package_id }}" style="margin: 0;" onsubmit="return confirm('Are you sure you want to delete this package?');">
                  <button type="submit" class="admin-btn admin-btn-danger" style="padding: 0.5rem 0.8rem; font-size: 0.9rem;">Delete</button>
                </form>
              </div>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>"""

html = re.sub(r'<table class="admin-table">.*?</table>', new_table, html, flags=re.DOTALL)

# Insert the script just before the closing body tag
js = """
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
            base64Output.value = evt.target.result;
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
</body>"""

html = html.replace('</body>', js)

with open(filepath, 'w') as f:
    f.write(html)
