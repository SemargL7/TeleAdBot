import React, {useEffect, useState} from "react";
import { useNavigate } from 'react-router-dom';
import tokenService from "../utils/tokenService";
import createAxiosInstance from "../utils/axios";


const Auth = () => {
  const [token, setToken] = useState(tokenService.getToken());
  const navigate = useNavigate();
  useEffect(() => {
    if (!token) {

      const urlParams = new URLSearchParams(window.location.search);
      const tokenParam = urlParams.get("token");
      if (tokenParam) {
        setToken(tokenParam);
      }
    }
  }, []);

  useEffect(() => {
    tokenService.setToken(token);
    const axios = createAxiosInstance();
    axios
      .get("get_self_user_info/")
      .then((response) => {
        console.log(response.data);
        tokenService.setUser(JSON.stringify(response.data));
        navigate('/');
      })
      .catch((error) => {
        console.log("Error fetching data: " + error);
      });
  }, [token]);

  return (
    <p>Auth</p>
  );
};

export default Auth;