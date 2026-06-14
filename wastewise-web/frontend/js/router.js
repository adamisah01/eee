import { state } from './state.js';

const appContainer = document.getElementById('app');

const routes = {
  '/': { template: '/templates/landing.html', script: '/js/pages/landing.js', protected: false, fullWidth: true },
  '/dashboard': { template: '/templates/home.html', script: '/js/pages/home.js', protected: true },
  '/login': { template: '/templates/auth/login.html', script: '/js/pages/auth/login.js', protected: false },
  '/otp': { template: '/templates/auth/otp.html', script: '/js/pages/auth/otp.js', protected: false },
  '/order/new': { template: '/templates/newOrder.html', script: '/js/pages/newOrder.js', protected: true },
  '/orders': { template: '/templates/orderHistory.html', script: '/js/pages/orderHistory.js', protected: true },
  '/profile': { template: '/templates/profile.html', script: '/js/pages/profile.js', protected: true },
  '/collector/dashboard': { template: '/templates/collector/dashboard.html', script: '/js/pages/collector/dashboard.js', protected: true },
  '/collector/job': { template: '/templates/collector/activeJob.html', script: '/js/pages/collector/activeJob.js', protected: true },
  '/collector/history': { template: '/templates/collector/jobHistory.html', script: '/js/pages/collector/jobHistory.js', protected: true },
  '/collector/earnings': { template: '/templates/collector/earnings.html', script: '/js/pages/collector/earnings.js', protected: true },
  '/collector/profile': { template: '/templates/collector/collectorProfile.html', script: '/js/pages/collector/collectorProfile.js', protected: true },
  '/admin/dashboard': { template: '/templates/admin/dashboard.html', script: '/js/pages/admin/dashboard.js', protected: false, fullWidth: true },
};

const loadTemplate = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to load template ${url}`);
    return await response.text();
  } catch (err) {
    return `<div class="page flex-col items-center justify-center"><h2>Error Loading Page</h2><p class="text-muted">${err.message}</p></div>`;
  }
};

export const router = async () => {
  let hash = window.location.hash.slice(1) || '/';
  
  let match = routes[hash];
  
  if (!match) {
    // Dynamic matching 
    if (hash.startsWith('/track/')) match = { template: '/templates/trackOrder.html', script: '/js/pages/trackOrder.js', protected: true };
    else if (hash.startsWith('/payment/')) match = { template: '/templates/payment.html', script: '/js/pages/payment.js', protected: true };
    else if (hash.startsWith('/order/')) match = { template: '/templates/orderDetail.html', script: '/js/pages/orderDetail.js', protected: true };
    else match = routes['/']; // fallback
  }

  // Auth Guard
  if (match.protected && !state.isLoggedIn()) {
    window.location.hash = '#/login';
    return;
  }

  // Toggle full-width layout
  if (match.fullWidth) {
    appContainer.classList.add('full-width');
  } else {
    appContainer.classList.remove('full-width');
  }

  // Render loader
  appContainer.innerHTML = '<div class="loader-container"><div class="spinner"></div></div>';
  
  // Render HTML
  const html = await loadTemplate(match.template);
  appContainer.innerHTML = html;

  // Execute Logic
  if (match.script) {
    try {
      const module = await import(match.script + '?t=' + Date.now()); 
      if (module.default && typeof module.default.init === 'function') {
        module.default.init();
      }
    } catch (e) {
      console.error('Error loading page script:', e);
    }
  }
};

window.addEventListener('hashchange', router);
