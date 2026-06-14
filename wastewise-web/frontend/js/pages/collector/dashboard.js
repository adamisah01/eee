export default {
  init: () => {
    let isOnline = false;
    const toggleBtn = document.getElementById('toggle-status-btn');
    const statusCard = document.getElementById('status-card');
    const noJobsMsg = document.getElementById('no-jobs-msg');
    const activeJobCard = document.getElementById('active-job-card');

    if(!toggleBtn) return;

    toggleBtn.addEventListener('click', () => {
      isOnline = !isOnline;
      if (isOnline) {
        if ('geolocation' in navigator) {
          navigator.geolocation.getCurrentPosition(() => {
            statusCard.className = 'collector-status online';
            statusCard.innerHTML = '🟢 You are Online';
            toggleBtn.textContent = 'Go Offline';
            toggleBtn.className = 'btn btn-outline';
            noJobsMsg.classList.add('hidden');
            
            // Simulate incoming job
            setTimeout(() => {
              window.showToast('🚨 New Job Available!', 'success');
              activeJobCard.classList.remove('hidden');
            }, 2500);
          }, () => {
            window.showToast('Location required to go online', 'error');
            isOnline = false;
          });
        }
      } else {
        statusCard.className = 'collector-status offline';
        statusCard.innerHTML = '⚫ You are Offline';
        toggleBtn.textContent = 'Go Online';
        toggleBtn.className = 'btn btn-primary';
        noJobsMsg.classList.remove('hidden');
        activeJobCard.classList.add('hidden');
      }
    });

    window.acceptJob = () => {
      window.location.hash = '#/collector/job';
    };

    window.declineJob = () => {
      activeJobCard.classList.add('hidden');
      noJobsMsg.classList.remove('hidden');
      noJobsMsg.textContent = 'Waiting for jobs...';
    };
  }
};
