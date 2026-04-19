const THEME_STORAGE_KEY = "ghoomnechalo-theme";
const MAX_SOURCE_IMAGE_BYTES = 15 * 1024 * 1024;
const SUPPORTED_UPLOAD_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
]);

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** exponent;
  return `${value.toFixed(value >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`;
}

function getCsrfToken(formElement) {
  return (
    formElement?.querySelector('input[name="csrf_token"]')?.value ||
    document.querySelector('input[name="csrf_token"]')?.value ||
    ""
  );
}

async function requestCloudinarySignature({ file, formElement }) {
  const csrfToken = getCsrfToken(formElement);
  if (!csrfToken) {
    throw new Error("Missing CSRF token. Refresh the page and try again.");
  }

  const packageId = formElement?.querySelector('input[name="package_id"]')?.value || "package-image";
  const response = await fetch("/admin/cloudinary-signature", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: JSON.stringify({
      filename: file.name,
      package_id: packageId,
    }),
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(payload?.detail || "Could not start the Cloudinary upload.");
  }

  return payload;
}

async function uploadImageToCloudinary({ file, formElement, statusElement, previewElement }) {
  if (!file) {
    throw new Error("Please choose an image first.");
  }

  if (!SUPPORTED_UPLOAD_TYPES.has(file.type)) {
    throw new Error("Use a JPG, PNG, WebP, or GIF image.");
  }

  if (file.size > MAX_SOURCE_IMAGE_BYTES) {
    throw new Error("Please choose an image that is 15 MB or smaller.");
  }

  if (statusElement) {
    statusElement.textContent = `Uploading ${file.name} (${formatBytes(file.size)}) to Cloudinary...`;
  }

  const localPreviewUrl = previewElement ? URL.createObjectURL(file) : null;
  if (previewElement && localPreviewUrl) {
    previewElement.src = localPreviewUrl;
    previewElement.classList.remove("is-hidden");
  }

  try {
    const signaturePayload = await requestCloudinarySignature({ file, formElement });
    const uploadFormData = new FormData();
    uploadFormData.append("file", file);
    uploadFormData.append("api_key", signaturePayload.api_key);
    uploadFormData.append("timestamp", String(signaturePayload.timestamp));
    uploadFormData.append("signature", signaturePayload.signature);
    uploadFormData.append("folder", signaturePayload.folder);
    uploadFormData.append("public_id", signaturePayload.public_id);
    uploadFormData.append("overwrite", String(signaturePayload.overwrite));
    uploadFormData.append("allowed_formats", signaturePayload.allowed_formats.join(","));
    uploadFormData.append("max_file_size", String(signaturePayload.max_file_size));

    const uploadResponse = await fetch(signaturePayload.upload_url, {
      method: "POST",
      body: uploadFormData,
    });
    const uploadPayload = await uploadResponse.json().catch(() => null);

    if (!uploadResponse.ok) {
      throw new Error(uploadPayload?.error?.message || "Cloudinary upload failed.");
    }

    if (!uploadPayload?.secure_url) {
      throw new Error("Cloudinary upload did not return a secure URL.");
    }

    if (previewElement) {
      previewElement.src = uploadPayload.secure_url;
      previewElement.classList.remove("is-hidden");
    }

    return {
      secureUrl: uploadPayload.secure_url,
      publicId: uploadPayload.public_id,
      bytes: uploadPayload.bytes ?? file.size,
      message: `Uploaded to Cloudinary: ${formatBytes(uploadPayload.bytes ?? file.size)}.`,
    };
  } finally {
    if (localPreviewUrl) {
      URL.revokeObjectURL(localPreviewUrl);
    }
  }
}

window.uploadImageToCloudinary = uploadImageToCloudinary;
window.formatUploadBytes = formatBytes;

function initChrome() {
  const navbar = document.querySelector(".navbar");
  const navToggle = document.querySelector("#nav-toggle");
  const themeToggle = document.querySelector("#theme-toggle");
  const navLinks = document.querySelectorAll(".nav-links a");

  const closeMobileMenu = () => {
    if (!navbar || !navToggle) {
      return;
    }
    navbar.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Open menu");
  };

  const openMobileMenu = () => {
    if (!navbar || !navToggle) {
      return;
    }
    navbar.classList.add("is-open");
    navToggle.setAttribute("aria-expanded", "true");
    navToggle.setAttribute("aria-label", "Close menu");
  };

  if (navToggle) {
    navToggle.addEventListener("click", () => {
      const isExpanded = navToggle.getAttribute("aria-expanded") === "true";
      if (isExpanded) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", closeMobileMenu);
  });

  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    document.body.dataset.theme = theme;
  };

  if (themeToggle) {
    themeToggle.addEventListener("click", (event) => {
      event.preventDefault();
      const currentTheme = document.body.dataset.theme || document.documentElement.dataset.theme || "dark";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    });
  }

  let lastScrollY = window.scrollY;
  window.addEventListener("scroll", () => {
    const currentScrollY = window.scrollY;
    if (currentScrollY > 100) {
      if (currentScrollY > lastScrollY && (!navbar || !navbar.classList.contains("is-open"))) {
        navbar?.classList.add("navbar--hidden");
      } else {
        navbar?.classList.remove("navbar--hidden");
      }
    } else {
      navbar?.classList.remove("navbar--hidden");
    }
    lastScrollY = currentScrollY;
  });
}

function initAdminTabs() {
  const buttons = document.querySelectorAll("[data-admin-tab-target]");
  const panels = document.querySelectorAll("[data-admin-panel]");

  if (!buttons.length || !panels.length) {
    return;
  }

  const setActiveTab = (name) => {
    buttons.forEach((button) => {
      button.classList.toggle("active", button.dataset.adminTabTarget === name);
    });

    panels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.adminPanel === name);
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => setActiveTab(button.dataset.adminTabTarget));
  });
}

function initAdminSearch() {
  const searchInput = document.getElementById("adminSearch");
  const rows = document.querySelectorAll("[data-package-row]");

  if (!searchInput || !rows.length) {
    return;
  }

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    rows.forEach((row) => {
      const haystack = `${row.dataset.packageId || ""} ${row.dataset.packageTitle || ""}`.toLowerCase();
      row.classList.toggle("is-hidden", Boolean(query) && !haystack.includes(query));
    });
  });
}

function initDeleteForms() {
  const forms = document.querySelectorAll(".js-delete-package-form");
  const loadingOverlay = document.getElementById("loadingOverlay");

  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      const approved = window.confirm("Are you sure you want to delete this package?");
      if (!approved) {
        event.preventDefault();
        return;
      }
      loadingOverlay?.classList.add("is-active");
    });
  });
}

function initImageFallbacks() {
  document.querySelectorAll(".js-image-preview").forEach((image) => {
    image.addEventListener("error", () => {
      image.classList.add("is-hidden");
    });
  });
}

function initAddPackageUpload() {
  const imageUpload = document.getElementById("imageUpload");
  const cardImageValue = document.getElementById("base64Output");
  const form = document.getElementById("addPackageForm");
  const loader = document.getElementById("loadingOverlay");
  const imageUploadStatus = document.getElementById("imageUploadStatus");
  let imageUploadInFlight = false;

  if (!imageUpload || !cardImageValue || !form) {
    return;
  }

  imageUpload.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    cardImageValue.value = "";

    if (!file) {
      if (imageUploadStatus) {
        imageUploadStatus.textContent = "Upload a file up to 15 MB. It will upload directly to Cloudinary.";
      }
      return;
    }

    if (imageUploadStatus) {
      imageUploadStatus.textContent = `Preparing ${file.name} (${formatBytes(file.size)})...`;
    }

    try {
      imageUploadInFlight = true;
      const uploadResult = await uploadImageToCloudinary({
        file,
        formElement: form,
        statusElement: imageUploadStatus,
      });
      cardImageValue.value = uploadResult.secureUrl;
      if (imageUploadStatus) {
        imageUploadStatus.textContent = uploadResult.message;
      }
    } catch (error) {
      imageUpload.value = "";
      cardImageValue.value = "";
      if (imageUploadStatus) {
        imageUploadStatus.textContent = error.message;
      }
      window.alert(error.message);
    } finally {
      imageUploadInFlight = false;
    }
  });

  form.addEventListener("submit", (event) => {
    if (imageUploadInFlight) {
      event.preventDefault();
      window.alert("Image upload is still in progress. Please wait a moment and try again.");
      return;
    }

    if (imageUpload.files.length > 0 && !cardImageValue.value) {
      event.preventDefault();
      window.alert("Please upload the image to Cloudinary before submitting.");
      return;
    }

    loader?.classList.add("is-active");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initChrome();
  initAdminTabs();
  initAdminSearch();
  initDeleteForms();
  initImageFallbacks();
  initAddPackageUpload();
});
