export default {
  init: () => {
    // Parse URL params for pre-selecting waste type
    const urlParams = new URLSearchParams(window.location.hash.split('?')[1]);
    const type = urlParams.get('type');
    
    if (type) {
      const radio = document.querySelector(`input[value="${type}"]`);
      if (radio) {
        radio.checked = true;
      }
    }
    updateRadioStyles(); // initial call

    // Bind events for radio buttons
    document.querySelectorAll('input[name="waste_type"]').forEach(input => {
      input.addEventListener('change', updateRadioStyles);
    });

    window.nextStep = (step) => {
      document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
      document.getElementById(`step-${step}`).classList.remove('hidden');
      
      // Update Stepper
      const s2 = document.getElementById('step2-indicator');
      const s3 = document.getElementById('step3-indicator');
      
      s2.style.background = step >= 2 ? 'var(--color-primary)' : 'var(--color-border)';
      s2.style.color = step >= 2 ? 'white' : 'var(--color-text-muted)';
      
      s3.style.background = step === 3 ? 'var(--color-primary)' : 'var(--color-border)';
      s3.style.color = step === 3 ? 'white' : 'var(--color-text-muted)';
      
      const line = document.getElementById('stepper-line');
      if (step === 1) line.style.width = '0%';
      if (step === 2) line.style.width = '50%';
      if (step === 3) line.style.width = '100%';

      if (step === 3) {
        // Populate summary
        const selectedType = document.querySelector('input[name="waste_type"]:checked').value;
        const typeLabel = selectedType === 'general' ? 'General Household' : 'Recyclable';
        document.getElementById('summary-type').textContent = typeLabel;
        document.getElementById('summary-address').textContent = document.getElementById('address').value;
        
        const schedEl = document.getElementById('schedule');
        document.getElementById('summary-schedule').textContent = schedEl.options[schedEl.selectedIndex].text;
      }
    };

    window.useLocation = () => {
      if ('geolocation' in navigator) {
        window.showToast('Fetching location...', 'info');
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            // Mock geocoding
            document.getElementById('address').value = '15 Opebi Road, Ikeja, Lagos';
            window.showToast('Location updated', 'success');
          },
          (err) => {
            window.showToast('Could not get location', 'error');
          }
        );
      }
    };

    window.confirmOrder = async () => {
      const btn = document.getElementById('confirm-btn');
      btn.disabled = true;
      btn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;border-top-color:white;"></div>';

      try {
        await new Promise(res => setTimeout(res, 1200));
        window.showToast('Order created successfully!', 'success');
        
        const orderId = 'WW' + Math.floor(10000000 + Math.random() * 90000000);
        window.location.hash = `#/track/${orderId}`;
      } catch (e) {
        window.showToast('Failed to create order', 'error');
        btn.disabled = false;
        btn.innerHTML = 'Confirm Pickup 🎉';
      }
    };

    function updateRadioStyles() {
      document.querySelectorAll('input[name="waste_type"]').forEach(input => {
        const card = input.closest('.card');
        if (input.checked) {
          card.style.borderColor = 'var(--color-primary)';
          card.style.background = 'var(--color-primary-light)';
        } else {
          card.style.borderColor = 'transparent';
          card.style.background = 'var(--color-surface)';
        }
      });
    }
  }
};
