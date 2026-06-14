export default {
  init: () => {
    // 1. Timer Logic
    let timeLeft = 24 * 60 * 60; // 24 hours in seconds
    const timerDisplay = document.getElementById('timer-display');
    const timerInterval = setInterval(() => {
      timeLeft--;
      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        timerDisplay.textContent = "00:00:00";
        return;
      }
      
      const h = Math.floor(timeLeft / 3600).toString().padStart(2, '0');
      const m = Math.floor((timeLeft % 3600) / 60).toString().padStart(2, '0');
      const s = (timeLeft % 60).toString().padStart(2, '0');
      timerDisplay.textContent = `${h}:${m}:${s}`;
    }, 1000);

    // 2. Pay Button Logic (Mock Paystack Inline)
    const payBtn = document.getElementById('pay-now-btn');
    if (payBtn) {
      payBtn.addEventListener('click', () => {
        payBtn.disabled = true;
        payBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;border-top-color:white;"></div>';
        
        // Mock Paystack popup interaction
        window.showToast('Opening secure payment gateway...', 'info');
        
        setTimeout(() => {
          // Mock successful payment return
          clearInterval(timerInterval);
          document.getElementById('pay-action').classList.add('hidden');
          document.getElementById('payment-header').classList.add('hidden');
          document.getElementById('success-state').classList.remove('hidden');
          
          window.showToast('Payment verified successfully!', 'success');
        }, 2000);
      });
    }
  }
};
