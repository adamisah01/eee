import { router } from './router.js';

// Global toast notification
window.showToast = (message, type = 'info') => {
  const container = document.getElementById('toast-container');
  if(!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('hiding');
    toast.addEventListener('animationend', () => toast.remove());
  }, 3000);
};

// Online/Offline detection
window.addEventListener('online', () => {
  const banner = document.getElementById('offline-banner');
  if(banner) banner.classList.add('hidden');
  window.showToast('Back online!', 'success');
});

window.addEventListener('offline', () => {
  const banner = document.getElementById('offline-banner');
  if(banner) banner.classList.remove('hidden');
});

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('SW registered!', reg.scope))
      .catch(err => console.error('SW registration failed:', err));
  });
}

// Init Router
document.addEventListener('DOMContentLoaded', () => {
  if (!navigator.onLine) {
    const banner = document.getElementById('offline-banner');
    if(banner) banner.classList.remove('hidden');
  }
  router();
});
