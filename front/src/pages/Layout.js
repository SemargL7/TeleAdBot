import React, { useEffect, useState } from "react";
import { Outlet, Link } from "react-router-dom";
import { Container, Navbar, Nav } from "react-bootstrap";
import tokenService from "../utils/tokenService";
import createAxiosInstance from "../utils/axios";

const Layout = () => {
  const [token, setToken] = useState(tokenService.getToken());

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
      })
      .catch((error) => {
        console.log("Error fetching data: " + error);
      });
  }, [token]);

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">
            TeleAdBot
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">
                Home
              </Nav.Link>
              <Nav.Link as={Link} to="/myads">
                My Ads
              </Nav.Link>
              <Nav.Link as={Link} to="/myOrders">
                My Orders
              </Nav.Link>
              <Nav.Link as={Link} to="/wallet">
                Wallet
              </Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container className="mt-4">
        <Outlet />
      </Container>
    </>
  );
};

export default Layout;