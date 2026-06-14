export default {
  init: () => {
    let step = 0;
    const btn = document.getElementById('action-btn');
    if(!btn) return;

    const steps = [
      { text: "I've Arrived", toast: "En Route to customer" },
      { text: "Start Collecting", toast: "Arrived at location. Please take a photo." },
      { text: "Mark Complete ✅", toast: "Collecting waste..." },
      { text: "Done", toast: "Job Completed! Customer notified to pay." }
    ];

    btn.addEventListener('click', async () => {
      window.showToast(steps[step].toast, 'info');
      
      if(step === 1) {
        // Trigger photo capture mock
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.capture = 'environment';
        fileInput.click();
      }

      step++;
      
      if (step < steps.length) {
        btn.textContent = steps[step].text;
      } else {
        btn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;border-top-color:white;"></div>';
        await new Promise(res => setTimeout(res, 1000));
        window.location.hash = '#/collector/dashboard';
      }
    });
  }
};
