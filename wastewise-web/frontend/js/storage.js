export const Storage = {
  get: (key) => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (e) { return null; }
  },
  set: (key, value) => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (e) { console.error('Error saving to localStorage', e); }
  },
  remove: (key) => {
    window.localStorage.removeItem(key);
  },
  getSession: (key) => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (e) { return null; }
  },
  setSession: (key, value) => {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (e) {}
  },
  removeSession: (key) => {
    window.sessionStorage.removeItem(key);
  }
};
