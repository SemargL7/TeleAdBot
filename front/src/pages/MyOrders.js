import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Container, Form, Button, Row, Col, ListGroup, Pagination } from "react-bootstrap";
import createAxiosInstance from "../utils/axios";
import tokenService from "../utils/tokenService";

const MyOrders = () => {
  const user = tokenService.getUser();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orderStatuses, setOrderStatuses] = useState([]);
  const [filters, setFilters] = useState({
    order_status: '',
    created_at_after: '',
    created_at_before: '',
    payment_time_after: '',
    payment_time_before: '',
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1
  });

  useEffect(() => {
    fetchOrders();
  }, [filters, pagination.currentPage]);

  useEffect(() => {
    fetchOrderStatuses();
  }, []);

  const fetchOrderStatuses = () => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.get(`/get_order_statuses/`)
      .then(response => {
        setOrderStatuses(response.data);
      })
      .catch(error => {
        console.log('Error fetching order statuses: ' + error);
      });
  };

  const fetchOrders = () => {
    setLoading(true);
    const axiosInstance = createAxiosInstance();
    const queryParams = new URLSearchParams({
      ...filters,
      page: pagination.currentPage
    }).toString();
    axiosInstance.get(`/get_my_orders/?${queryParams}`)
      .then(response => {
        setOrders(response.data.results);
        setPagination({
          currentPage: pagination.currentPage,
          totalPages: Math.ceil(response.data.count / 10)
        });
        setLoading(false);
      })
      .catch(error => {
        console.log('Error fetching orders: ' + error);
        setLoading(false);
      });
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleResetFilters = () => {
    setFilters({
      order_status: '',
      created_at_after: '',
      created_at_before: '',
      payment_time_after: '',
      payment_time_before: '',
    });
    setPagination({
      ...pagination,
      currentPage: 1
    });
  };

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= pagination.totalPages) {
      setPagination({
        ...pagination,
        currentPage: newPage
      });
    }
  };

  return (
    <Container>
      <h1>My Orders</h1>
      <div>
        <h3>Filters</h3>
        <Form>
          <Row className="mb-3">
            <Col md={3}>
              <Form.Group controlId="orderStatus">
                <Form.Label>Status</Form.Label>
                <Form.Control
                  as="select"
                  name="order_status"
                  value={filters.order_status}
                  onChange={handleFilterChange}
                >
                  <option value="">All</option>
                  {orderStatuses.map(status => (
                    <option key={status.order_status} value={status.order_status}>
                      {status.order_status_name}
                    </option>
                  ))}
                </Form.Control>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="createdAtAfter">
                <Form.Label>Created After</Form.Label>
                <Form.Control
                  type="datetime-local"
                  name="created_at_after"
                  value={filters.created_at_after}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="createdAtBefore">
                <Form.Label>Created Before</Form.Label>
                <Form.Control
                  type="datetime-local"
                  name="created_at_before"
                  value={filters.created_at_before}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="paymentTimeAfter">
                <Form.Label>Payment After</Form.Label>
                <Form.Control
                  type="datetime-local"
                  name="payment_time_after"
                  value={filters.payment_time_after}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="paymentTimeBefore">
                <Form.Label>Payment Before</Form.Label>
                <Form.Control
                  type="datetime-local"
                  name="payment_time_before"
                  value={filters.payment_time_before}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
          </Row>
          <Button variant="primary" onClick={() => setPagination({ ...pagination, currentPage: 1 })}>
            Apply Filters
          </Button>
          <Button variant="secondary" onClick={handleResetFilters} className="ml-2">
            Reset Filters
          </Button>
        </Form>
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          {orders.length === 0 ? (
            <p>No orders found.</p>
          ) : (
            <ListGroup>
              {orders.map(order => (
                <ListGroup.Item key={order.order_id}>
                  <Row>
                    <Col md={2}>
                      <strong>Order ID:</strong> {order.order_id}
                    </Col>
                    <Col md={2}>
                      <strong>Side:</strong> {order.taker == user.user_id ? "Taker" : "Maker"}
                    </Col>
                    <Col md={3}>
                      <strong>Created at:</strong> {new Date(order.created_at).toLocaleString()}
                    </Col>
                    <Col md={2}>
                      <Link to={`order?order_id=${order.order_id}`} className="btn btn-primary">
                        View Details
                      </Link>
                    </Col>
                  </Row>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
          <Pagination className="mt-3">
            <Pagination.Prev
              onClick={() => handlePageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
            />
            {[...Array(pagination.totalPages)].map((_, index) => (
              <Pagination.Item
                key={index}
                active={index + 1 === pagination.currentPage}
                onClick={() => handlePageChange(index + 1)}
              >
                {index + 1}
              </Pagination.Item>
            ))}
            <Pagination.Next
              onClick={() => handlePageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage === pagination.totalPages}
            />
          </Pagination>
        </div>
      )}
    </Container>
  );
};

export default MyOrders;