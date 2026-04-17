// edit.js
document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const base64Output = document.getElementById('base64Output');
    const imagePreview = document.getElementById('currentImagePreview');

    if (imageUpload && base64Output) {
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    base64Output.value = evt.target.result;
                    if (imagePreview) {
                        imagePreview.src = evt.target.result;
                        imagePreview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Cancel Button Confirmation
    const cancelBtn = document.querySelector('.btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
                e.preventDefault();
            }
        });
    }

    // Auto-resize Textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // trigger initial resize if it has content
        if(textarea.value.trim() !== '') {
            setTimeout(() => {
                textarea.style.height = 'auto';
                textarea.style.height = (textarea.scrollHeight) + 'px';
            }, 100);
        }
    });

    // Form Submit Loading Overlay
    const editForm = document.getElementById('editPackageForm');
    const loader = document.getElementById('loadingOverlay');
    if (editForm && loader) {
        editForm.addEventListener('submit', () => {
            loader.classList.add('is-active');
        });
    }
});
