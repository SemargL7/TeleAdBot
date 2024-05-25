import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Container, Card, Button, Row, Col, ListGroup } from "react-bootstrap";
import createAxiosInstance from "../utils/axios";

const MyAds = () => {
  const [ads, setAds] = useState([]);

  useEffect(() => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.get('/get_user_ads/')
      .then(response => {
        setAds(response.data);
      })
      .catch(error => {
        console.error('Error fetching data', error);
      });
  }, []);

  const handleStatusToggle = (adId, isActive) => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/advertisement_status_switch/', { ad_id: adId, is_active: !isActive })
      .then(response => {
        setAds(ads.map(ad => ad.ad_id === adId ? { ...ad, is_active: !isActive } : ad));
      })
      .catch(error => {
        console.error('Error toggling status:', error);
      });
  };

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>My Ads</h1>
        <Button as={Link} to="/myads/create" variant="primary">
          Create New Ad
        </Button>
      </div>
      {ads.length === 0 ? (
        <p>No advertisements found.</p>
      ) : (
        <Row>
          {ads.map(ad => (
            <Col md={6} lg={4} key={ad.ad_id} className="mb-4">
              <Card>
                <Card.Body>
                  <Card.Title>{ad.chat.title}</Card.Title>
                  <Card.Subtitle className="mb-2 text-muted">
                    Created by: {ad.created_by.first_name}
                  </Card.Subtitle>
                  <Card.Text>
                    <strong>Description:</strong> {ad.description}
                  </Card.Text>
                  <ListGroup variant="flush">
                    <ListGroup.Item><strong>Created at:</strong> {new Date(ad.created_at).toLocaleString()}</ListGroup.Item>
                    <ListGroup.Item><strong>Updated at:</strong> {new Date(ad.updated_at).toLocaleString()}</ListGroup.Item>
                    <ListGroup.Item><strong>Active:</strong> {ad.is_active ? "Yes" : "No"}</ListGroup.Item>
                    <ListGroup.Item>
                      <strong>Options:</strong>
                      <ul>
                        {ad.options.map((option, index) => (
                          <li key={index}>
                            {option.advertisement_option_type.advertisement_option_type_name}: ${option.price} ({option.currency.name})
                          </li>
                        ))}
                      </ul>
                    </ListGroup.Item>
                  </ListGroup>
                  <Button
                    variant={ad.is_active ? "danger" : "success"}
                    onClick={() => handleStatusToggle(ad.ad_id, ad.is_active)}
                    className="mt-2"
                  >
                    {ad.is_active ? "Deactivate" : "Activate"}
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default MyAds;