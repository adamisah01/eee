import { state } from '../state.js';

export default {
  init: () => {
    const userNameEl = document.getElementById('user-name');
    if (userNameEl && state.user) {
      userNameEl.textContent = state.user.name || 'User';
    }
  }
};
