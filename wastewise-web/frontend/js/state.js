import { Storage } from './storage.js';

class AppState {
  constructor() {
    this.user = Storage.get('ww_user') || null;
    this.token = Storage.get('ww_token') || null;
    this.listeners = [];
  }

  setUser(user, token) {
    this.user = user;
    this.token = token;
    if (user) {
      Storage.set('ww_user', user);
      if(token) Storage.set('ww_token', token);
    } else {
      Storage.remove('ww_user');
      Storage.remove('ww_token');
    }
    this.notify();
  }

  isLoggedIn() {
    return !!this.token;
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this));
  }
}

export const state = new AppState();
