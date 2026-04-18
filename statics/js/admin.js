
const THEME_STORAGE_KEY = 'ghoomnechalo-theme';

function initAdmin() {
  const navbar = document.querySelector('.navbar');
  const navToggle = document.querySelector('#nav-toggle');
  const themeToggle = document.querySelector('#theme-toggle');
  
  const closeMobileMenu = () => {
    if (navbar == null || navToggle == null) return;
    navbar.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open menu');
  };

  const openMobileMenu = () => {
    if (navbar == null || navToggle == null) return;
    navbar.classList.add('is-open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Close menu');
  };

  if (navToggle) {
    navToggle.addEventListener('click', () => {
      const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
      if (isExpanded) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  const applyTheme = (theme) => {
    document.body.dataset.theme = theme;
  };

  const toggleTheme = (e) => {
    e.preventDefault();
    const currentTheme = document.body.dataset.theme || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  };

  if (themeToggle) {
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    const defaultTheme = storedTheme || (prefersLight ? 'light' : 'dark');
    applyTheme(defaultTheme);

    themeToggle.addEventListener('click', toggleTheme);
  }

  let lastScrollY = window.scrollY;
  window.addEventListener('scroll', () => {
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

document.addEventListener('DOMContentLoaded', () => {
  initAdmin();
});
