const TOKEN_KEY = 'auth_token';
const USER = 'user';

const tokenService = {
  setToken: (token) => {
    localStorage.setItem(TOKEN_KEY, token);
  },

  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  removeToken: () => {
    localStorage.removeItem(TOKEN_KEY);
  },

  setUser: (user) => {
    localStorage.setItem(USER, user);
  },
  getUser: () => {
    const user = localStorage.getItem(USER);
    return user ? JSON.parse(user) : null; // Parse the JSON string back to an object
  },
  removeUser: () => {
    localStorage.removeItem(USER);
  }
};

export default tokenService;