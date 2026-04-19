// edit.js
document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const cardImageValue = document.getElementById('base64Output');
    const imagePreview = document.getElementById('currentImagePreview');
    const imageUploadStatus = document.getElementById('imageUploadStatus');
    const editForm = document.getElementById('editPackageForm');
    let imageUploadInFlight = false;

    if (imageUpload && cardImageValue) {
        imageUpload.addEventListener('change', async function(e) {
            const file = e.target.files[0];
            cardImageValue.value = '';

            if (!file) {
                if (imageUploadStatus) {
                    imageUploadStatus.textContent = 'Upload a file up to 15 MB. It will upload directly to Cloudinary.';
                }
                return;
            }

            if (imageUploadStatus) {
                imageUploadStatus.textContent = `Preparing ${file.name} (${window.formatUploadBytes ? window.formatUploadBytes(file.size) : file.size + ' bytes'})...`;
            }

            try {
                imageUploadInFlight = true;
                const uploadResult = await window.uploadImageToCloudinary({
                    file,
                    formElement: editForm,
                    statusElement: imageUploadStatus,
                    previewElement: imagePreview,
                });
                cardImageValue.value = uploadResult.secureUrl;
                imagePreview?.classList.remove('is-hidden');

                if (imageUploadStatus) {
                    imageUploadStatus.textContent = uploadResult.message;
                }
            } catch (error) {
                imageUpload.value = '';
                cardImageValue.value = '';

                if (imageUploadStatus) {
                    imageUploadStatus.textContent = error.message;
                }

                alert(error.message);
            } finally {
                imageUploadInFlight = false;
            }
        });
    }

    if (imagePreview) {
        imagePreview.addEventListener('error', () => {
            imagePreview.classList.add('is-hidden');
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
            this.style.height = `${this.scrollHeight}px`;
        });
        
        // trigger initial resize if it has content
        if(textarea.value.trim() !== '') {
            setTimeout(() => {
                textarea.style.height = 'auto';
                textarea.style.height = `${textarea.scrollHeight}px`;
            }, 100);
        }
    });

    // Form Submit Loading Overlay
    const loader = document.getElementById('loadingOverlay');
    if (editForm && loader) {
        editForm.addEventListener('submit', (e) => {
            if (imageUploadInFlight) {
                e.preventDefault();
                alert('Image upload is still in progress. Please wait a moment and try again.');
                return;
            }
            if (imageUpload && imageUpload.files.length > 0 && !cardImageValue.value) {
                e.preventDefault();
                alert('Image upload did not finish. Please upload the image again.');
                return;
            }
            loader.classList.add('is-active');
        });
    }
});
