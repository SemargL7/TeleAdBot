import React, { useState, useEffect } from 'react';
import createAxiosInstance from '../utils/axios';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Form, Button, Card, Spinner, Pagination } from 'react-bootstrap';

const Home = () => {
  const [onlineAds, setOnlineAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatTypes, setChatTypes] = useState([]);
  const [filters, setFilters] = useState({
    chat_type: '',
    description: '',
    page: 1,
  });

  useEffect(() => {
    fetchAds();
    fetchChatTypes();
  }, [filters]);

  const fetchChatTypes = () => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.get('/get_chat_types/')
      .then(response => {
        setChatTypes(response.data);
      })
      .catch(error => {
        console.log('Error fetching chat types: ' + error);
      });
  };

  const fetchAds = () => {
    setLoading(true);
    const axiosInstance = createAxiosInstance();
    const queryParams = new URLSearchParams(filters).toString();
    axiosInstance.get(`/get_online_ads/?${queryParams}`)
      .then(response => {
        setOnlineAds(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.log('Error fetching data: ' + error);
        setLoading(false);
      });
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value,
      page: 1,
    });
  };

  const handlePageChange = (newPage) => {
    setFilters({
      ...filters,
      page: newPage,
    });
  };

  return (
    <Container className="mt-5">
      <h1 className="mb-4">Online Advertisements</h1>
      <div>
        <h3>Filters</h3>
        <Form>
          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Chat Type:</Form.Label>
                <Form.Control as="select" name="chat_type" value={filters.chat_type} onChange={handleFilterChange}>
                  <option value="">All</option>
                  {chatTypes.map(type => (
                    <option key={type.chat_type_id} value={type.chat_type_name}>{type.chat_type_name}</option>
                  ))}
                </Form.Control>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Description:</Form.Label>
                <Form.Control type="text" name="description" value={filters.description} onChange={handleFilterChange} />
              </Form.Group>
            </Col>
            <Col md={4} className="d-flex align-items-end">
              <Button variant="primary" onClick={fetchAds} className="me-2">Apply Filters</Button>
              <Button variant="secondary" onClick={() => setFilters({ chat_type: '', description: '', page: 1 })}>Reset Filters</Button>
            </Col>
          </Row>
        </Form>
      </div>

      {loading ? (
        <div className="text-center mt-5">
          <Spinner animation="border" />
        </div>
      ) : (
        <div>
          {onlineAds.results.length === 0 ? (
            <p>No advertisements found.</p>
          ) : (
            <Row>
              {onlineAds.results.map(ad => (
                <Col md={6} lg={4} key={ad.ad_id}>
                  <Card className="mb-4">
                    <Card.Body>
                      <Card.Title>{ad.chat.title}</Card.Title>
                      <Card.Subtitle className="mb-2 text-muted">Chat type: {ad.chat.chat_type.chat_type_name}</Card.Subtitle>
                      <Card.Text>
                        {ad.options.map(op => (
                          <div key={op.advertisement_option_type.advertisement_option_type}>
                            <strong>Type:</strong> {op.advertisement_option_type.advertisement_option_type_name}<br />
                            <strong>Price:</strong> ${op.price}
                          </div>
                        ))}
                      </Card.Text>
                      <Link to={`createOrder?ad_id=${ad.ad_id}`} className="btn btn-primary">Create Order</Link>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
          <Pagination>
            {onlineAds.previous && (
              <Pagination.Prev onClick={() => handlePageChange(filters.page - 1)} />
            )}
            <Pagination.Item active>{filters.page}</Pagination.Item>
            {onlineAds.next && (
              <Pagination.Next onClick={() => handlePageChange(filters.page + 1)} />
            )}
          </Pagination>
        </div>
      )}
    </Container>
  );
};

export default Home;