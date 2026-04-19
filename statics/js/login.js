document.addEventListener("DOMContentLoaded", () => {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.getElementById("password-toggle");
  const eyeOpen = document.getElementById("eye-open");
  const eyeClosed = document.getElementById("eye-closed");

  if (!passwordInput || !toggleButton || !eyeOpen || !eyeClosed) {
    return;
  }

  toggleButton.addEventListener("click", () => {
    const isPassword = passwordInput.getAttribute("type") === "password";
    passwordInput.setAttribute("type", isPassword ? "text" : "password");
    toggleButton.setAttribute("aria-pressed", String(isPassword));
    eyeOpen.classList.toggle("is-hidden", isPassword);
    eyeClosed.classList.toggle("is-hidden", !isPassword);
  });
});
