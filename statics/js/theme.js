(function () {
  const storageKey = "ghoomnechalo-theme";
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const storedTheme = window.localStorage.getItem(storageKey);
  const theme = storedTheme || (prefersDark ? "dark" : "light");

  document.documentElement.dataset.theme = theme;

  const applyToBody = () => {
    if (document.body) {
      document.body.dataset.theme = theme;
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyToBody, { once: true });
  } else {
    applyToBody();
  }
})();
