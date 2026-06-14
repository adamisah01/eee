import { state } from '../state.js';
export default {
  init: () => {
    const nameEl = document.getElementById('profile-name');
    if (nameEl && state.user) {
      nameEl.textContent = state.user.name || 'User';
    }
  }
};
