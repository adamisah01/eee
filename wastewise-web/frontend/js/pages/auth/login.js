import { Storage } from '../../storage.js';

export default {
  init: () => {
    const form = document.getElementById('login-form');
    const btn = document.getElementById('login-btn');
    
    if(!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const phoneInput = document.getElementById('phone').value.trim();
      if (!phoneInput) return;

      btn.disabled = true;
      btn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;border-top-color:white;"></div>';

      try {
        // Simulating API network request
        await new Promise(res => setTimeout(res, 800));
        
        Storage.setSession('ww_pending_phone', `+234${phoneInput}`);
        window.showToast('OTP sent to your phone', 'success');
        window.location.hash = '#/otp';
      } catch (err) {
        window.showToast(err.message || 'Error occurred', 'error');
        btn.disabled = false;
        btn.innerHTML = 'Get OTP';
      }
    });
  }
};
