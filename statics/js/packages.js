const THEME_STORAGE_KEY = "ghoomnechalo-theme";
let PACKAGE_DETAILS = {};

async function fetchPackages() {
  try {
    const res = await fetch("/api/packages");
    if (res.ok) {
      PACKAGE_DETAILS = await res.json();
    }
  } catch (error) {
    console.error("Failed to fetch packages", error);
  }
}

function initPackages() {
  const navbar = document.querySelector(".navbar");
  const navToggle = document.querySelector("#nav-toggle");
  const themeToggle = document.querySelector("#theme-toggle");
  
  // Menu logic
  const closeMobileMenu = () => {
    if (!navbar || !navToggle) return;
    navbar.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Open menu");
  };

  const openMobileMenu = () => {
    if (!navbar || !navToggle) return;
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

  // Theme logic
  const applyTheme = (theme) => {
    document.body.dataset.theme = theme;
  };

  const toggleTheme = (e) => {
    e.preventDefault();
    const currentTheme = document.body.dataset.theme || "dark";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  };

  if (themeToggle) {
    // Initial theme setup
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    const defaultTheme = storedTheme || (prefersDark ? "dark" : "light");
    applyTheme(defaultTheme);

    themeToggle.addEventListener("click", toggleTheme);
  }

  // Modal logic
  const packageTriggers = document.querySelectorAll("[data-package-trigger]");
  const packageModal = document.querySelector("#package-modal");
  const packageCloseTriggers = document.querySelectorAll("[data-package-close]");
  const packageTabs = document.querySelectorAll("[data-package-tab]");
  const packagePanels = document.querySelectorAll("[data-package-panel]");

  // Reused elements
  const els = {
    image: document.querySelector("#package-modal-image"),
    eyebrow: document.querySelector("#package-modal-eyebrow"),
    title: document.querySelector("#package-modal-title"),
    summary: document.querySelector("#package-modal-summary"),
    facts: document.querySelector("#package-modal-facts"),
    flow: document.querySelector("#package-modal-flow"),
    highlights: document.querySelector("#package-modal-highlights"),
    inclusions: document.querySelector("#package-modal-inclusions"),
    exclusions: document.querySelector("#package-modal-exclusions"),
    carry: document.querySelector("#package-modal-carry"),
    book: document.querySelector("#package-modal-book"),
  };

  const WHATSAPP_NUMBER = "919536309897";

  const buildList = (items) => items.map((item) => `<li>${item}</li>`).join("");

  const openModal = (packageId) => {
    const details = PACKAGE_DETAILS[packageId];
    if (!details || !packageModal) return;

    if (els.eyebrow) els.eyebrow.textContent = details.eyebrow;
    if (els.title) els.title.textContent = details.title;
    if (els.summary) els.summary.textContent = details.summary;
    if (els.image) {
      els.image.src = details.image;
      els.image.alt = `${details.title} cover image`;
    }
    if (els.facts) {
      els.facts.innerHTML = (details.facts || [])
        .map((fact) => `<span class="package-modal__fact">${fact}</span>`)
        .join("");
    }
    if (els.flow) {
      els.flow.innerHTML = (details.itinerary || [])
        .map(
          (day) => `
        <div class="package-modal__flowstep">
          <div class="package-modal__flowday">${day.day}</div>
          <div class="package-modal__flowinfo">
            <h5 class="package-modal__flowtitle">${day.title}</h5>
            <ul class="package-modal__flowlist">
              ${buildList(day.items || [])}
            </ul>
          </div>
        </div>
      `
        )
        .join("");
    }
    if (els.highlights) els.highlights.innerHTML = buildList(details.highlights || []);
    if (els.inclusions) els.inclusions.innerHTML = buildList(details.inclusions || []);
    if (els.exclusions) els.exclusions.innerHTML = buildList(details.exclusions || []);
    if (els.carry) els.carry.innerHTML = buildList(details.carry || []);
    
    if (els.book) {
      const msg = encodeURIComponent(`Hi, I'm interested in the ${details.title} package.`);
      els.book.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${msg}`;
    }

    // Reset tabs to first
    packageTabs.forEach((tab) => {
      tab.classList.remove("is-active");
      tab.setAttribute("aria-selected", "false");
    });
    packagePanels.forEach((panel) => panel.classList.remove("is-active"));
    
    if (packageTabs[0]) {
      packageTabs[0].classList.add("is-active");
      packageTabs[0].setAttribute("aria-selected", "true");
    }
    if (packagePanels[0]) packagePanels[0].classList.add("is-active");

    packageModal.classList.add("is-open");
    packageModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  };

  const closeModal = () => {
    if (!packageModal) return;
    packageModal.classList.remove("is-open");
    packageModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (els.image) els.image.src = "";
  };

  packageTriggers.forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn.dataset.packageTrigger));
  });

  packageCloseTriggers.forEach((btn) => {
    btn.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && packageModal && packageModal.classList.contains("is-open")) {
      closeModal();
    }
  });
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
  packageTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.packageTab;
      packageTabs.forEach((t) => {
        t.classList.remove("is-active");
        t.setAttribute("aria-selected", "false");
      });
      packagePanels.forEach((p) => p.classList.remove("is-active"));

      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      
      const panel = document.querySelector(`[data-package-panel="${target}"]`);
      if (panel) panel.classList.add("is-active");
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await fetchPackages();
  initPackages();
});
