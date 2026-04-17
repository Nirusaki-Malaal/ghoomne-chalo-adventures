import * as THREE from "three";

const WHATSAPP_NUMBER = "919536309897";
const THEME_STORAGE_KEY = "ghoomnechalo-theme";
const HERO_ART = {
  dark: {
    desktop: "./statics/assets/horizontal.jpg",
    mobile: "./statics/assets/vertical_foreground.png",
  },
  light: {
    desktop: "./statics/assets/horizontal_light.png",
    mobile: "./statics/assets/vertical_foreground_light.png",
  },
};

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

// Call immediately to preload packages
fetchPackages();

function createSeededRandom(seed) {
  let value = seed % 2147483647;

  if (value <= 0) {
    value += 2147483646;
  }

  return () => {
    value = (value * 16807) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

function createMoonTexture(size = 1024) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext("2d");
  const center = size / 2;
  const radius = size * 0.44;
  const random = createSeededRandom(1977);

  ctx.clearRect(0, 0, size, size);

  const baseGradient = ctx.createRadialGradient(
    center - radius * 0.2,
    center - radius * 0.24,
    radius * 0.16,
    center,
    center,
    radius
  );
  baseGradient.addColorStop(0, "#faf8f2");
  baseGradient.addColorStop(0.48, "#ddd8cf");
  baseGradient.addColorStop(0.78, "#a79f96");
  baseGradient.addColorStop(1, "#5f5b58");

  ctx.fillStyle = baseGradient;
  ctx.beginPath();
  ctx.arc(center, center, radius, 0, Math.PI * 2);
  ctx.fill();

  ctx.save();
  ctx.beginPath();
  ctx.arc(center, center, radius, 0, Math.PI * 2);
  ctx.clip();

  for (let i = 0; i < 720; i += 1) {
    const angle = random() * Math.PI * 2;
    const distance = Math.sqrt(random()) * radius * 0.98;
    const x = center + Math.cos(angle) * distance;
    const y = center + Math.sin(angle) * distance;
    const dotSize = radius * (0.003 + random() * 0.008);
    const alpha = 0.02 + random() * 0.055;

    ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
    ctx.beginPath();
    ctx.arc(x, y, dotSize, 0, Math.PI * 2);
    ctx.fill();
  }

  for (let i = 0; i < 90; i += 1) {
    const angle = random() * Math.PI * 2;
    const distance = Math.sqrt(random()) * radius * 0.84;
    const x = center + Math.cos(angle) * distance;
    const y = center + Math.sin(angle) * distance;
    const craterRadius = radius * (0.03 + random() * 0.085);

    const shadow = ctx.createRadialGradient(
      x + craterRadius * 0.25,
      y + craterRadius * 0.25,
      craterRadius * 0.12,
      x,
      y,
      craterRadius
    );
    shadow.addColorStop(0, `rgba(68, 63, 62, ${0.12 + random() * 0.18})`);
    shadow.addColorStop(0.7, `rgba(86, 81, 78, ${0.06 + random() * 0.14})`);
    shadow.addColorStop(1, "rgba(0, 0, 0, 0)");

    ctx.fillStyle = shadow;
    ctx.beginPath();
    ctx.arc(x, y, craterRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = `rgba(255, 255, 255, ${0.04 + random() * 0.08})`;
    ctx.lineWidth = craterRadius * 0.12;
    ctx.beginPath();
    ctx.arc(x - craterRadius * 0.09, y - craterRadius * 0.09, craterRadius * 0.72, 0, Math.PI * 2);
    ctx.stroke();
  }

  const terminator = ctx.createLinearGradient(
    center - radius,
    center,
    center + radius * 0.85,
    center
  );
  terminator.addColorStop(0, "rgba(12, 14, 18, 0.52)");
  terminator.addColorStop(0.36, "rgba(12, 14, 18, 0.08)");
  terminator.addColorStop(0.62, "rgba(255, 255, 255, 0.05)");
  terminator.addColorStop(1, "rgba(255, 255, 255, 0)");

  ctx.fillStyle = terminator;
  ctx.fillRect(center - radius, center - radius, radius * 2, radius * 2);

  const rimLight = ctx.createRadialGradient(
    center - radius * 0.24,
    center - radius * 0.28,
    radius * 0.06,
    center,
    center,
    radius
  );
  rimLight.addColorStop(0, "rgba(255, 255, 255, 0.22)");
  rimLight.addColorStop(0.55, "rgba(255, 255, 255, 0.05)");
  rimLight.addColorStop(1, "rgba(255, 255, 255, 0)");

  ctx.fillStyle = rimLight;
  ctx.fillRect(center - radius, center - radius, radius * 2, radius * 2);

  ctx.restore();

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;

  return texture;
}

function createGlowTexture(size = 512) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext("2d");
  const center = size / 2;
  const radius = size * 0.46;

  const glow = ctx.createRadialGradient(center, center, radius * 0.08, center, center, radius);
  glow.addColorStop(0, "rgba(245, 248, 255, 0.9)");
  glow.addColorStop(0.24, "rgba(214, 228, 255, 0.44)");
  glow.addColorStop(0.56, "rgba(143, 176, 255, 0.12)");
  glow.addColorStop(1, "rgba(143, 176, 255, 0)");

  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, size, size);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;

  return texture;
}

function createStarParticleTexture(size = 128) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext("2d");
  const center = size / 2;
  const radius = size * 0.5;
  const glow = ctx.createRadialGradient(center, center, 0, center, center, radius);

  glow.addColorStop(0, "rgba(255, 255, 255, 1)");
  glow.addColorStop(0.2, "rgba(255, 255, 255, 0.98)");
  glow.addColorStop(0.46, "rgba(237, 243, 255, 0.66)");
  glow.addColorStop(0.74, "rgba(196, 212, 255, 0.18)");
  glow.addColorStop(1, "rgba(196, 212, 255, 0)");

  ctx.clearRect(0, 0, size, size);
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, size, size);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;

  return texture;
}

function createStarField(count, config) {
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const particleTexture = createStarParticleTexture();

  for (let i = 0; i < count; i += 1) {
    const index = i * 3;
    const radius = THREE.MathUtils.randFloat(config.radius.min, config.radius.max);
    const angle = Math.random() * Math.PI * 2;
    const spread = Math.pow(Math.random(), config.verticalBias);

    positions[index] = Math.cos(angle) * radius;
    positions[index + 1] = THREE.MathUtils.lerp(config.height.min, config.height.max, spread);
    positions[index + 2] = THREE.MathUtils.randFloat(config.depth.min, config.depth.max);

    const color = new THREE.Color().setHSL(
      THREE.MathUtils.randFloat(config.hue.min, config.hue.max),
      THREE.MathUtils.randFloat(config.saturation.min, config.saturation.max),
      THREE.MathUtils.randFloat(config.lightness.min, config.lightness.max)
    );

    colors[index] = color.r;
    colors[index + 1] = color.g;
    colors[index + 2] = color.b;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: config.size,
    map: particleTexture,
    alphaMap: particleTexture,
    sizeAttenuation: true,
    transparent: true,
    alphaTest: 0.08,
    opacity: config.opacity,
    depthWrite: false,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
  });

  const points = new THREE.Points(geometry, material);
  points.position.set(config.offset.x, config.offset.y, config.offset.z);

  return { points, material, geometry, texture: particleTexture };
}

function setupSpaceScene(spaceLayer, prefersReducedMotion) {
  if (!spaceLayer) {
    return null;
  }

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  });

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
  renderer.setClearColor(0x000000, 0);
  spaceLayer.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 2, 18);

  const moonGroup = new THREE.Group();
  moonGroup.position.set(6.3, 6.7, -6.4);
  moonGroup.scale.setScalar(0.92);

  const moonTexture = createMoonTexture(1024);
  const glowTexture = createGlowTexture(512);

  const moon = new THREE.Mesh(
    new THREE.SphereGeometry(1.55, 64, 64),
    new THREE.MeshStandardMaterial({
      map: moonTexture,
      roughness: 0.96,
      metalness: 0,
      emissive: 0xb7c9f2,
      emissiveIntensity: 0.05,
    })
  );

  const moonHalo = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture,
      transparent: true,
      opacity: prefersReducedMotion ? 0.18 : 0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      depthTest: false,
    })
  );
  moonHalo.scale.set(6.8, 6.8, 1);

  const moonLight = new THREE.PointLight(0xd7e4ff, 14, 60, 2);
  moonLight.position.set(-1.4, 1.1, 2.6);

  const moonFill = new THREE.AmbientLight(0x5f759f, 0.55);

  moonGroup.add(moonHalo);
  moonGroup.add(moonLight);
  moonGroup.add(moon);
  scene.add(moonFill);
  scene.add(moonGroup);

  const starRig = new THREE.Group();
  scene.add(starRig);

  const distantField = createStarField(prefersReducedMotion ? 320 : 520, {
    radius: { min: 6, max: 18 },
    height: { min: -1.5, max: 13 },
    depth: { min: -10, max: -2 },
    size: 0.12,
    opacity: 0.85,
    verticalBias: 0.52,
    offset: { x: 0, y: 0, z: 0 },
    hue: { min: 0.54, max: 0.64 },
    saturation: { min: 0.15, max: 0.45 },
    lightness: { min: 0.72, max: 0.96 },
  });

  const nearField = createStarField(prefersReducedMotion ? 120 : 220, {
    radius: { min: 4, max: 15 },
    height: { min: -2.2, max: 11.5 },
    depth: { min: -4, max: 2 },
    size: 0.2,
    opacity: 0.95,
    verticalBias: 0.62,
    offset: { x: 0.4, y: -0.2, z: 0.4 },
    hue: { min: 0.52, max: 0.63 },
    saturation: { min: 0.1, max: 0.38 },
    lightness: { min: 0.8, max: 1 },
  });

  starRig.add(distantField.points);
  starRig.add(nearField.points);

  const shootingStar = new THREE.Group();
  shootingStar.visible = false;

  const tailMaterial = new THREE.LineBasicMaterial({
    color: 0xcfe5ff,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const tailGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(-0.75, 0.08, 0),
    new THREE.Vector3(-1.8, 0.2, 0),
    new THREE.Vector3(-3.2, 0.38, 0),
  ]);

  const tail = new THREE.Line(tailGeometry, tailMaterial);

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.08, 12, 12),
    new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );

  shootingStar.add(tail);
  shootingStar.add(head);
  scene.add(shootingStar);

  const nebula = new THREE.Mesh(
    new THREE.PlaneGeometry(26, 18),
    new THREE.MeshBasicMaterial({
      color: 0x6b8cff,
      transparent: true,
      opacity: 0.06,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );
  nebula.position.set(0, 2, -12);
  scene.add(nebula);

  const sizeScene = () => {
    const { clientWidth, clientHeight } = spaceLayer;

    if (!clientWidth || !clientHeight) {
      return;
    }

    camera.aspect = clientWidth / clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(clientWidth, clientHeight, false);
  };

  sizeScene();

  let rafId = 0;
  let lastTime = 0;
  let shootingCooldown = prefersReducedMotion ? 8.5 : 4.6;
  let shootingProgress = 0;
  let shootingDuration = 0;
  let shootingStart = new THREE.Vector3();
  let shootingEnd = new THREE.Vector3();

  const launchShootingStar = () => {
    shootingProgress = 0;
    shootingDuration = THREE.MathUtils.randFloat(0.85, 1.35);
    shootingCooldown = THREE.MathUtils.randFloat(3.8, 7.4);

    shootingStart = new THREE.Vector3(
      THREE.MathUtils.randFloat(6, 12),
      THREE.MathUtils.randFloat(5, 9),
      THREE.MathUtils.randFloat(-2, 2)
    );

    shootingEnd = new THREE.Vector3(
      THREE.MathUtils.randFloat(-8, -2),
      THREE.MathUtils.randFloat(0.5, 3.4),
      THREE.MathUtils.randFloat(-2, 2)
    );

    shootingStar.position.copy(shootingStart);
    shootingStar.rotation.z = Math.atan2(
      shootingEnd.y - shootingStart.y,
      shootingEnd.x - shootingStart.x
    );
    shootingStar.visible = true;
    tailMaterial.opacity = 0.95;
    head.material.opacity = 1;
  };

  const animate = (time) => {
    const seconds = time * 0.001;
    const delta = lastTime ? seconds - lastTime : 0.016;
    lastTime = seconds;

    if (!prefersReducedMotion) {
      moonGroup.position.y = 6.7 + Math.sin(seconds * 0.16) * 0.16;
      moonGroup.rotation.z = Math.sin(seconds * 0.08) * 0.03;
      moon.rotation.y += delta * 0.12;
      moonHalo.material.opacity = 0.14 + Math.sin(seconds * 1.1) * 0.04;
      moonHalo.scale.setScalar(6.8 + Math.sin(seconds * 0.7) * 0.16);
      starRig.rotation.z += delta * 0.018;
      starRig.rotation.x = Math.sin(seconds * 0.12) * 0.035;
      nearField.points.rotation.z -= delta * 0.02;
      nearField.points.rotation.y = Math.sin(seconds * 0.1) * 0.04;
      distantField.material.opacity = 0.74 + Math.sin(seconds * 0.9) * 0.07;
      nearField.material.opacity = 0.88 + Math.cos(seconds * 1.4) * 0.06;
      nebula.rotation.z += delta * 0.006;

      shootingCooldown -= delta;

      if (!shootingStar.visible && shootingCooldown <= 0) {
        launchShootingStar();
      }

      if (shootingStar.visible) {
        shootingProgress += delta / shootingDuration;

        const eased = THREE.MathUtils.smootherstep(shootingProgress, 0, 1);
        shootingStar.position.lerpVectors(shootingStart, shootingEnd, eased);

        tailMaterial.opacity = 0.95 - eased * 0.65;
        head.material.opacity = 1 - eased * 0.4;

        if (shootingProgress >= 1) {
          shootingStar.visible = false;
        }
      }
    }

    renderer.render(scene, camera);
    rafId = window.requestAnimationFrame(animate);
  };

  rafId = window.requestAnimationFrame(animate);
  window.addEventListener("resize", sizeScene);

  return {
    renderer,
    starRig,
    moonGroup,
    moonHalo,
    destroy() {
      window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", sizeScene);
      distantField.geometry.dispose();
      nearField.geometry.dispose();
      distantField.material.dispose();
      nearField.material.dispose();
      distantField.texture.dispose();
      nearField.texture.dispose();
      moon.geometry.dispose();
      moon.material.map.dispose();
      moon.material.dispose();
      moonHalo.material.map.dispose();
      moonHalo.material.dispose();
      tailGeometry.dispose();
      tailMaterial.dispose();
      head.geometry.dispose();
      head.material.dispose();
      nebula.geometry.dispose();
      nebula.material.dispose();
      renderer.dispose();
      spaceLayer.innerHTML = "";
    },
  };
}

window.addEventListener("load", () => {
  const gsapInstance = window.gsap;
  const ScrollTriggerPlugin = window.ScrollTrigger;

  if (!gsapInstance || !ScrollTriggerPlugin) {
    return;
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  gsapInstance.registerPlugin(ScrollTriggerPlugin);

  const heroPanel = document.querySelector(".hero-panel");
  const heroCopy = document.querySelector(".hero-copy");
  const heroEyebrow = document.querySelector(".hero-eyebrow");
  const heroText = document.querySelector(".hero-text");
  const heroSubtext = document.querySelector(".hero-subtext");
  const heroBase = document.querySelector(".base");
  const heroSun = document.querySelector(".hero-sun");
  const foreground = document.querySelector(".foreground-layer");
  const spaceLayer = document.querySelector(".space-layer");
  const scrollCue = document.querySelector(".scroll-cue");
  const navbar = document.querySelector(".navbar");
  const navToggle = document.querySelector("#nav-toggle");
  const navLinks = document.querySelectorAll(".nav-links a");
  const themeToggle = document.querySelector("#theme-toggle");
  const reviewsGrid = document.querySelector(".reviews-grid");
  const packageCards = gsapInstance.utils.toArray(".package-card");
  const packageTriggers = document.querySelectorAll("[data-package-trigger]");
  const packageModal = document.querySelector("#package-modal");
  const packageModalImage = document.querySelector("#package-modal-image");
  const packageModalEyebrow = document.querySelector("#package-modal-eyebrow");
  const packageModalTitle = document.querySelector("#package-modal-title");
  const packageModalSummary = document.querySelector("#package-modal-summary");
  const packageModalFacts = document.querySelector("#package-modal-facts");
  const packageModalBook = document.querySelector("#package-modal-book");
  const packageModalFlow = document.querySelector("#package-modal-flow");
  const packageModalHighlights = document.querySelector("#package-modal-highlights");
  const packageModalInclusions = document.querySelector("#package-modal-inclusions");
  const packageModalExclusions = document.querySelector("#package-modal-exclusions");
  const packageModalCarry = document.querySelector("#package-modal-carry");
  const packageModalContent = document.querySelector(".package-modal__scroll");
  const packageTabs = document.querySelectorAll("[data-package-tab]");
  const packagePanels = document.querySelectorAll("[data-package-panel]");
  const packageCloseTriggers = document.querySelectorAll("[data-package-close]");
  const photoCards = gsapInstance.utils.toArray(".photo-card");
  let spaceScene = null;
  let heroScrollTimeline = null;

  if (!heroPanel || !heroCopy || !heroText || !heroBase || !foreground || !spaceLayer) {
    return;
  }

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

  const getCurrentTheme = () => {
    return document.body.dataset.theme === "light" ? "light" : "dark";
  };

  const updateThemeToggle = (theme) => {
    if (!themeToggle) {
      return;
    }

    const nextMode = theme === "light" ? "Dark" : "Light";
    themeToggle.setAttribute("aria-label", `Switch to ${nextMode.toLowerCase()} mode`);
    themeToggle.setAttribute("aria-pressed", String(theme === "light"));
  };

  const getViewportMetrics = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;

    return {
      width,
      height,
      isPhone: width <= 640,
      isTablet: width <= 1024,
      isCompactHeight: height <= 560,
      isLandscape: width > height,
    };
  };

  const enableDesktopReviewWheelScroll = () => {
    if (!reviewsGrid) {
      return;
    }

    reviewsGrid.addEventListener(
      "wheel",
      (event) => {
        if (window.innerWidth <= 720) {
          return;
        }

        const canScrollHorizontally = reviewsGrid.scrollWidth > reviewsGrid.clientWidth;

        if (!canScrollHorizontally || Math.abs(event.deltaY) <= Math.abs(event.deltaX)) {
          return;
        }

        event.preventDefault();
        reviewsGrid.scrollLeft += event.deltaY;
      },
      { passive: false },
    );
  };

  const getHeroScrollConfig = () => {
    const viewport = getViewportMetrics();

    if (viewport.isPhone) {
      const isCompactPhone = viewport.isLandscape || viewport.isCompactHeight;

      return {
        pinDistance: Math.round(viewport.height * (isCompactPhone ? 1.55 : 2.15)),
        copyYPercent: isCompactPhone ? -44 : -58,
        copyAutoAlpha: isCompactPhone ? 0.2 : 0.14,
        scrollCueYPercent: isCompactPhone ? -58 : -72,
        baseScale: isCompactPhone ? 1.04 : 1.06,
        baseYPercent: isCompactPhone ? -2 : -4,
        baseFilter: isCompactPhone ? "brightness(0.72)" : "brightness(0.7)",
        spaceYPercent: isCompactPhone ? -4 : -6,
        foregroundRestYPercent: 14,
        foregroundRestScale: 1,
        foregroundYPercent: 14,
        foregroundScale: 1,
        starRigZ: 0.1,
        starRigX: 0.04,
        moonX: 4.4,
        moonY: 3.8,
        moonScale: 0.98,
        sunYPercent: isCompactPhone ? -10 : -16,
        sunScale: 1.01,
      };
    }

    if (viewport.isTablet) {
      return {
        pinDistance: Math.round(viewport.height * 1.82),
        copyYPercent: -64,
        copyAutoAlpha: 0.12,
        scrollCueYPercent: -80,
        baseScale: 1.07,
        baseYPercent: -5,
        baseFilter: "brightness(0.68)",
        spaceYPercent: -8,
        foregroundRestYPercent: 12,
        foregroundRestScale: 1.01,
        foregroundYPercent: -12,
        foregroundScale: 1.1,
        starRigZ: 0.14,
        starRigX: 0.06,
        moonX: 5.9,
        moonY: 4.8,
        moonScale: 1.01,
        sunYPercent: -20,
        sunScale: 1.05,
      };
    }

    return {
      pinDistance: Math.round(viewport.height * 1.7),
      copyYPercent: -74,
      copyAutoAlpha: 0.08,
      scrollCueYPercent: -90,
      baseScale: 1.08,
      baseYPercent: -6,
      baseFilter: "brightness(0.64)",
      spaceYPercent: -10,
      foregroundRestYPercent: 16,
      foregroundRestScale: 1.02,
      foregroundYPercent: -18,
      foregroundScale: 1.16,
      starRigZ: 0.18,
      starRigX: 0.08,
      moonX: 7.2,
      moonY: 5.9,
      moonScale: 1.04,
      sunYPercent: -24,
      sunScale: 1.08,
    };
  };

  enableDesktopReviewWheelScroll();

  const getCardScrollConfig = () => {
    const viewport = getViewportMetrics();

  if (viewport.isPhone) {
      return {
        revealY: 34,
        revealRotateX: -4,
        revealStart: "top 94%",
        parallaxScale: 0,
        disableReveal: true,
      };
    }

    if (viewport.isTablet) {
      return {
        revealY: 52,
        revealRotateX: -8,
        revealStart: "top 88%",
        parallaxScale: 0.66,
        disableReveal: false,
      };
    }

    return {
      revealY: 70,
      revealRotateX: -10,
      revealStart: "top 84%",
      parallaxScale: 1,
      disableReveal: false,
    };
  };

  const getPhotoCardScrollConfig = () => {
    const viewport = getViewportMetrics();

    if (viewport.isPhone) {
      return {
        revealY: 30,
        revealRotateX: -3,
        revealStart: "top 94%",
      };
    }

    if (viewport.isTablet) {
      return {
        revealY: 42,
        revealRotateX: -6,
        revealStart: "top 88%",
      };
    }

    return {
      revealY: 56,
      revealRotateX: -8,
      revealStart: "top 82%",
    };
  };

  const syncResponsiveHeroState = () => {
    const heroScrollConfig = getHeroScrollConfig();

    gsapInstance.set(foreground, {
      xPercent: -50,
      yPercent: heroScrollConfig.foregroundRestYPercent,
      scale: heroScrollConfig.foregroundRestScale,
      transformOrigin: "center bottom",
    });
  };

  const updateHeroArt = () => {
    const theme = getCurrentTheme();
    const isMobile = window.innerWidth <= 640;
    const nextSource = isMobile ? HERO_ART[theme].mobile : HERO_ART[theme].desktop;

    if (heroBase.getAttribute("src") !== nextSource) {
      heroBase.setAttribute("src", nextSource);
    }

    heroBase.setAttribute(
      "alt",
      isMobile ? "Mountain landscape background mobile artwork" : "Mountain landscape background"
    );

    foreground.style.display = isMobile ? "none" : "";
  };

  const updateSpaceTheme = () => {
    if (!spaceScene) {
      return;
    }

    const isLightTheme = getCurrentTheme() === "light";
    spaceScene.moonGroup.visible = !isLightTheme;
    spaceScene.starRig.visible = !isLightTheme;
  };

  const applyTheme = (theme, options = {}) => {
    const nextTheme = theme === "light" ? "light" : "dark";
    const isLightTheme = nextTheme === "light";

    document.body.dataset.theme = nextTheme;
    updateThemeToggle(nextTheme);
    updateHeroArt();
    updateSpaceTheme();

    if (heroSun) {
      gsapInstance.set(heroSun, {
        clearProps: "opacity,visibility,transform",
      });
      gsapInstance.set(heroSun, {
        autoAlpha: isLightTheme ? 0.94 : 0,
        scale: isLightTheme ? 1 : 0.76,
        yPercent: 0,
        transformOrigin: "center center",
      });
    }

    if (heroScrollTimeline) {
      heroScrollTimeline.invalidate();
      ScrollTriggerPlugin.refresh();
    }

    if (!options.skipStorage) {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    }
  };

  const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  applyTheme(storedTheme || "dark", { skipStorage: true });

  themeToggle?.addEventListener("click", () => {
    applyTheme(getCurrentTheme() === "light" ? "dark" : "light");
  });

  window.addEventListener("resize", updateHeroArt);

  navToggle?.addEventListener("click", () => {
    if (!navbar?.classList.contains("is-open")) {
      openMobileMenu();
      return;
    }

    closeMobileMenu();
  });

  navLinks.forEach((link) => {
    link.addEventListener("click", closeMobileMenu);
  });

  document.addEventListener("click", (event) => {
    if (!navbar || !navToggle || !navbar.classList.contains("is-open")) {
      return;
    }

    if (navbar.contains(event.target)) {
      return;
    }

    closeMobileMenu();
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 640) {
      closeMobileMenu();
    }
  });

  const renderPackageList = (target, items) => {
    if (!target) {
      return;
    }

    target.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
  };

  const renderPackageFlow = (target, steps) => {
    if (!target) {
      return;
    }

    target.innerHTML = steps
      .map(
        (step) => `
          <article class="package-modal__flowstep">
            <p class="package-modal__flowday">${step.day}</p>
            <h4 class="package-modal__flowtitle">${step.title}</h4>
            <ul class="package-modal__flowlist">
              ${step.items.map((item) => `<li>${item}</li>`).join("")}
            </ul>
          </article>
        `
      )
      .join("");
  };

  const setActivePackageTab = (tabName) => {
    packageTabs.forEach((tab) => {
      const isActive = tab.getAttribute("data-package-tab") === tabName;
      tab.classList.toggle("is-active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
    });

    packagePanels.forEach((panel) => {
      const isActive = panel.getAttribute("data-package-panel") === tabName;
      panel.classList.toggle("is-active", isActive);

      if (isActive) {
        panel.scrollTop = 0;
      }
    });
  };

  const openPackageModal = (packageId) => {
    const details = PACKAGE_DETAILS[packageId];

    if (!details || !packageModal) {
      return;
    }

    packageModal.classList.add("is-open");
    packageModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    if (packageModalImage) {
      packageModalImage.src = details.image;
      packageModalImage.alt = `${details.title} package visual`;
    }

    if (packageModalEyebrow) {
      packageModalEyebrow.textContent = details.eyebrow;
    }

    if (packageModalTitle) {
      packageModalTitle.textContent = details.title;
    }

    if (packageModalSummary) {
      packageModalSummary.textContent = details.summary;
    }

    if (packageModalFacts) {
      packageModalFacts.innerHTML = details.facts.map((fact) => `<span>${fact}</span>`).join("");
    }

    if (packageModalBook) {
      const bookingMessage = encodeURIComponent(`I want to book this "${details.title}"`);
      packageModalBook.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${bookingMessage}`;
      packageModalBook.setAttribute("aria-label", `Book ${details.title} on WhatsApp`);
    }

    renderPackageFlow(packageModalFlow, details.itinerary);
    renderPackageList(packageModalHighlights, details.highlights);
    renderPackageList(packageModalInclusions, details.inclusions);
    renderPackageList(packageModalExclusions, details.exclusions);
    renderPackageList(packageModalCarry, details.carry);
    setActivePackageTab("flow");

    if (packageModalContent) {
      packageModalContent.scrollTop = 0;
    }
  };

  const closePackageModal = () => {
    if (!packageModal) {
      return;
    }

    packageModal.classList.remove("is-open");
    packageModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  };

  packageTriggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const packageId = trigger.getAttribute("data-package-trigger");
      openPackageModal(packageId);
    });
  });

  packageCloseTriggers.forEach((trigger) => {
    trigger.addEventListener("click", closePackageModal);
  });

  packageTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      setActivePackageTab(tab.getAttribute("data-package-tab"));
    });
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePackageModal();
    }
  });

  spaceScene = setupSpaceScene(spaceLayer, prefersReducedMotion);
  updateSpaceTheme();
  syncResponsiveHeroState();
  ScrollTriggerPlugin.addEventListener("refreshInit", syncResponsiveHeroState);

  if (heroSun) {
    gsapInstance.set(heroSun, {
      transformOrigin: "center center",
    });
  }

  if (!prefersReducedMotion) {
    const introTimeline = gsapInstance.timeline({ defaults: { ease: "power3.out" } });

    introTimeline
      .fromTo(
        spaceScene ? spaceScene.moonGroup.scale : { x: 0.72, y: 0.72, z: 0.72 },
        { x: 0.72, y: 0.72, z: 0.72 },
        { x: 0.92, y: 0.92, z: 0.92, duration: 1.15 },
        0
      )
      .fromTo(
        spaceScene ? spaceScene.moonHalo.material : { opacity: 0 },
        { opacity: 0 },
        { opacity: 0.18, duration: 1.2 },
        0.05
      )
      .fromTo(
        heroEyebrow,
        { autoAlpha: 0, y: 24, filter: "blur(10px)" },
        { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.8 }
      , 0.3)
      .fromTo(
        heroText,
        { autoAlpha: 0, y: 46, filter: "blur(14px)", letterSpacing: "-0.06em" },
        { autoAlpha: 1, y: 0, filter: "blur(0px)", letterSpacing: "0em", duration: 1.2 },
        "-=0.35"
      )
      .fromTo(
        heroSubtext,
        { autoAlpha: 0, y: 22, filter: "blur(10px)" },
        { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.9 },
        "-=0.7"
      )
      .fromTo(
        scrollCue,
        { autoAlpha: 0, y: 16 },
        { autoAlpha: 1, y: 0, duration: 0.8 },
        "-=0.45"
      );
  } else {
    gsapInstance.set([heroEyebrow, heroText, heroSubtext, scrollCue], {
      autoAlpha: 1,
      clearProps: "all",
    });
  }

  heroScrollTimeline = gsapInstance.timeline()
    .to(heroCopy, {
      yPercent: () => getHeroScrollConfig().copyYPercent,
      autoAlpha: () => getHeroScrollConfig().copyAutoAlpha,
      ease: "none",
    }, 0)
    .to(scrollCue, {
      yPercent: () => getHeroScrollConfig().scrollCueYPercent,
      autoAlpha: 0,
      ease: "none",
    }, 0)
    .to(heroBase, {
      scale: () => getHeroScrollConfig().baseScale,
      yPercent: () => getHeroScrollConfig().baseYPercent,
      filter: () => getHeroScrollConfig().baseFilter,
      ease: "none",
    }, 0)
    .to(spaceLayer, {
      yPercent: () => getHeroScrollConfig().spaceYPercent,
      opacity: 1,
      ease: "none",
    }, 0)
    .to(foreground, {
      yPercent: () => getHeroScrollConfig().foregroundYPercent,
      scale: () => getHeroScrollConfig().foregroundScale,
      ease: "none",
    }, 0)
    .to(spaceScene ? spaceScene.starRig.rotation : {}, {
      z: () => getHeroScrollConfig().starRigZ,
      x: () => getHeroScrollConfig().starRigX,
      ease: "none",
    }, 0)
    .to(spaceScene ? spaceScene.moonGroup.position : {}, {
      x: () => getHeroScrollConfig().moonX,
      y: () => getHeroScrollConfig().moonY,
      ease: "none",
    }, 0)
    .to(spaceScene ? spaceScene.moonGroup.scale : {}, {
      x: () => getHeroScrollConfig().moonScale,
      y: () => getHeroScrollConfig().moonScale,
      z: () => getHeroScrollConfig().moonScale,
      ease: "none",
    }, 0);

  if (heroSun) {
    heroScrollTimeline.to(heroSun, {
      yPercent: () => getHeroScrollConfig().sunYPercent,
      scale: () => getHeroScrollConfig().sunScale,
      autoAlpha: 0,
      ease: "none",
    }, 0);
  }

  ScrollTriggerPlugin.create({
    trigger: heroPanel,
    start: "top top",
    end: () => `+=${getHeroScrollConfig().pinDistance}`,
    pin: true,
    anticipatePin: 1,
    scrub: prefersReducedMotion ? false : 1.1,
    animation: heroScrollTimeline,
    invalidateOnRefresh: true,
  });

  if (!prefersReducedMotion) {
    packageCards.forEach((card, index) => {
      const glow = card.querySelector(".package-card__glow");
      const media = card.querySelector(".package-card__media img");
      const inner = card.querySelector(".package-card__inner");
      const content = card.querySelector(".package-card__content");
      const parallaxAmount = Number(card.dataset.parallax || 0.12);
      const cardScrollConfig = getCardScrollConfig();

      if (cardScrollConfig.disableReveal) {
        gsapInstance.set(card, { autoAlpha: 1, clearProps: "transform" });

        if (glow) {
          gsapInstance.set(glow, { clearProps: "transform,opacity" });
        }

        if (media) {
          gsapInstance.set(media, { clearProps: "transform" });
        }

        if (inner) {
          gsapInstance.set(inner, { clearProps: "transform" });
        }

        if (content) {
          gsapInstance.set(content, { clearProps: "transform" });
        }

        return;
      }

      gsapInstance.fromTo(
        card,
        {
          autoAlpha: 0,
          y: () => cardScrollConfig.revealY,
          rotateX: () => cardScrollConfig.revealRotateX,
        },
        {
          autoAlpha: 1,
          y: 0,
          rotateX: 0,
          duration: 1,
          delay: index * 0.08,
          ease: "power3.out",
          scrollTrigger: {
            trigger: card,
            start: () => getCardScrollConfig().revealStart,
            once: true,
            invalidateOnRefresh: true,
          },
        }
      );

      gsapInstance.fromTo(
        card,
        { yPercent: 0 },
        {
          yPercent: () => -parallaxAmount * 42 * getCardScrollConfig().parallaxScale,
          ease: "none",
          scrollTrigger: {
            trigger: card,
            start: "top bottom",
            end: "bottom top",
            scrub: 1.1,
            invalidateOnRefresh: true,
          },
        }
      );

      if (glow) {
        gsapInstance.fromTo(
          glow,
          { xPercent: -8, yPercent: 0, scale: 0.92, opacity: 0.45 },
          {
            xPercent: () => 10 * getCardScrollConfig().parallaxScale,
            yPercent: () => -18 * getCardScrollConfig().parallaxScale,
            scale: () => 0.92 + (0.2 * getCardScrollConfig().parallaxScale),
            opacity: () => 0.45 + (0.37 * getCardScrollConfig().parallaxScale),
            ease: "none",
            scrollTrigger: {
              trigger: card,
              start: "top bottom",
              end: "bottom top",
              scrub: 1.2,
              invalidateOnRefresh: true,
            },
          }
        );
      }

      if (media) {
        gsapInstance.fromTo(
          media,
          { yPercent: -4, scale: 1.08 },
          {
            yPercent: () => parallaxAmount * 26 * getCardScrollConfig().parallaxScale,
            scale: () => 1.08 + (0.08 * getCardScrollConfig().parallaxScale),
            ease: "none",
            scrollTrigger: {
              trigger: card,
              start: "top bottom",
              end: "bottom top",
              scrub: 1.1,
              invalidateOnRefresh: true,
            },
          }
        );
      }

      if (inner) {
        gsapInstance.fromTo(
          inner,
          { y: 0 },
          {
            y: () => parallaxAmount * 24 * getCardScrollConfig().parallaxScale,
            ease: "none",
            scrollTrigger: {
              trigger: card,
              start: "top bottom",
              end: "bottom top",
              scrub: 1,
              invalidateOnRefresh: true,
            },
          }
        );
      }

      if (content) {
        gsapInstance.fromTo(
          content,
          { y: 0 },
          {
            y: () => parallaxAmount * 14 * getCardScrollConfig().parallaxScale,
            ease: "none",
            scrollTrigger: {
              trigger: card,
              start: "top bottom",
              end: "bottom top",
              scrub: 1,
              invalidateOnRefresh: true,
            },
          }
        );
      }
    });

    photoCards.forEach((card, index) => {
      gsapInstance.fromTo(
        card,
        {
          autoAlpha: 0,
          y: () => getPhotoCardScrollConfig().revealY,
          rotateX: () => getPhotoCardScrollConfig().revealRotateX,
        },
        {
          autoAlpha: 1,
          y: 0,
          rotateX: 0,
          duration: 1,
          delay: index * 0.08,
          ease: "power3.out",
          scrollTrigger: {
            trigger: card,
            start: () => getPhotoCardScrollConfig().revealStart,
            once: true,
            invalidateOnRefresh: true,
          },
        }
      );
    });
  }

  window.addEventListener("beforeunload", () => {
    ScrollTriggerPlugin.removeEventListener("refreshInit", syncResponsiveHeroState);

    if (spaceScene) {
      spaceScene.destroy();
    }
  });

  ScrollTriggerPlugin.refresh();
});
