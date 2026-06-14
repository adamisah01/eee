import { Storage } from '../../storage.js';
import { state } from '../../state.js';

export default {
  init: () => {
    const phone = Storage.getSession('ww_pending_phone');
    if (!phone) {
      window.location.hash = '#/login';
      return;
    }

    const phoneDisplay = document.getElementById('otp-phone-display');
    if(phoneDisplay) phoneDisplay.textContent = phone;

    const container = document.getElementById('otp-container');
    const inputs = container ? Array.from(container.querySelectorAll('.otp-digit')) : [];
    const btn = document.getElementById('verify-btn');
    
    if(!inputs.length) return;

    const checkComplete = () => {
      const code = inputs.map(i => i.value).join('');
      btn.disabled = code.length !== 6;
      if(code.length === 6) {
        submitOtp(code);
      }
    };

    inputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
        if(e.target.value && index < inputs.length - 1) {
          inputs[index + 1].focus();
        }
        checkComplete();
      });

      input.addEventListener('keydown', (e) => {
        if(e.key === 'Backspace' && !e.target.value && index > 0) {
          inputs[index - 1].focus();
        }
      });
      
      // Handle paste
      input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData).getData('text').slice(0, 6).replace(/\D/g, '');
        pasted.split('').forEach((char, i) => {
          if(inputs[i]) {
            inputs[i].value = char;
            if(i < 5) inputs[i+1].focus();
          }
        });
        checkComplete();
      });
    });

    const submitOtp = async (code) => {
      btn.disabled = true;
      btn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;border-top-color:white;"></div>';

      try {
        // Mock network request
        await new Promise(res => setTimeout(res, 800));
        
        // Mock User & Token since API is not provided yet
        const mockUser = { id: 1, phone, name: 'Amaka', role: 'customer' };
        const mockToken = 'mock_jwt_token_123';
        
        state.setUser(mockUser, mockToken);
        Storage.removeSession('ww_pending_phone');
        
        window.showToast('Login successful!', 'success');
        window.location.hash = '#/'; // Go to home
      } catch (err) {
        window.showToast(err.message || 'Verification failed', 'error');
        btn.disabled = false;
        btn.innerHTML = 'Verify';
        inputs.forEach(i => i.value = '');
        inputs[0].focus();
      }
    };

    btn.addEventListener('click', () => {
      const code = inputs.map(i => i.value).join('');
      if(code.length === 6) submitOtp(code);
    });

    document.getElementById('resend-btn')?.addEventListener('click', () => {
      window.showToast('New OTP sent!', 'info');
      inputs.forEach(i => i.value = '');
      inputs[0].focus();
      btn.disabled = true;
    });
  }
};
