import axios from 'axios';
import tokenService from './tokenService'
const createAxiosInstance = () => {
  const instance = axios.create({
    baseURL: 'http://192.168.0.119:8000/api/v1', // Replace with your API base URL
    headers: {
      'Authorization': `Token ${tokenService.getToken()}`,
    },
  });

  return instance;
};

export default createAxiosInstance;
