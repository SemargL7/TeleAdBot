import React, { useEffect, useState } from "react";
import { Container, Row, Col, Button, ListGroup, Card, Spinner } from "react-bootstrap";
import createAxiosInstance from "../utils/axios";
import moment from "moment-timezone";
import tokenService from "../utils/tokenService";

const OrderDetails = () => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timezone, setTimezone] = useState(moment.tz.guess());
  const user = tokenService.getUser()

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const orderIdParam = urlParams.get('order_id');

    const axiosInstance = createAxiosInstance();
    axiosInstance.get(`/get_order/${orderIdParam}/`)
      .then(response => {
        setOrder(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.log('Error fetching data: ' + error);
        setLoading(false);
      });
  }, []);

  const handleAcceptOrder = (orderId) => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/confirm_order/', { order_id: orderId, confirm: true })
      .then(response => {
        alert('Order accepted successfully!');
        setOrder({ ...order, order_status: 'Accepted' });
      })
      .catch(error => {
        console.log('Error accepting order: ' + error);
        alert('Failed to accept order.');
      });
  };

  const handleCancelOrder = (orderId) => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/confirm_order/', { order_id: orderId, confirm: false }) // Replace with your API endpoint
      .then(response => {
        alert('Order canceled successfully!');
        setOrder({ ...order, order_status: 4 });
      })
      .catch(error => {
        console.log('Error canceling order: ' + error);
        alert('Failed to cancel order.');
      });
  };

  return (
    <Container>
      {loading ? (
        <div className="d-flex justify-content-center align-items-center" style={{ height: "80vh" }}>
          <Spinner animation="border" role="status">
            <span className="sr-only">Loading...</span>
          </Spinner>
        </div>
      ) : (
        <div>
          {order === null ? (
            <p>No order found.</p>
          ) : (
            <Card className="mt-4">
              <Card.Body>
                <Card.Title>Order Details</Card.Title>
                <Row>
                  <Col><strong>Order ID:</strong> {order.order_id}</Col>
                  <Col><strong>Advertisement Chat:</strong> {order.advertisement.chat.title}</Col>
                </Row>
                <Row className="mt-2">
                  <Col><strong>Taker:</strong> {order.taker.first_name}</Col>
                  <Col><strong>Status:</strong> {order.order_status.order_status_name}</Col>
                </Row>
                <Row className="mt-2">
                  <Col><strong>Created At:</strong> {moment.tz(order.created_at, timezone).format()}</Col>
                  <Col><strong>Payment Time:</strong> {moment.tz(order.payment_time, timezone).format()}</Col>
                </Row>
                {order.expired_at && (
                  <Row className="mt-2">
                    <Col><strong>Expired At:</strong> {moment.tz(order.expired_at, timezone).format()}</Col>
                  </Row>
                )}
                {order.finished_at && (
                  <Row className="mt-2">
                    <Col><strong>Finished At:</strong> {moment.tz(order.finished_at, timezone).format()}</Col>
                  </Row>
                )}

                {order.order_status.order_status === 1 && order.taker.user_id !== user.user_id &&(
                  <Row className="mt-3">
                    <Col>
                      <Button
                        variant="success"
                        className="mr-2"
                        onClick={() => handleAcceptOrder(order.order_id)}
                        disabled={order.order_status.order_status !== 1}
                      >
                        Accept
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleCancelOrder(order.order_id)}
                      >
                        Cancel
                      </Button>
                    </Col>
                  </Row>
                )}
                <h3 className="mt-4">Options</h3>
                <ListGroup>
                  {order.options.map(option => (
                    <ListGroup.Item key={option.id}>
                      <Row>
                        <Col><strong>Type:</strong> {option.advertisement_option.advertisement_option_type.advertisement_option_type_name}</Col>
                        <Col><strong>Price:</strong> {option.advertisement_option.price}</Col>
                        <Col><strong>Currency:</strong> {option.advertisement_option.currency.name}</Col>
                      </Row>
                      <Row className="mt-2">
                        <Col><strong>Scheduled At:</strong> {moment.tz(option.scheduledAt, timezone).format()}</Col>
                      </Row>
                      <Row className="mt-2">
                        <Col><strong>Post Data:</strong> {JSON.stringify(option.post_data)}</Col>
                      </Row>
                      <Row className="mt-2">
                        <Col><strong>Is Posted:</strong> {option.is_posted ? 'Yes' : 'No'}</Col>
                      </Row>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          )}
        </div>
      )}
    </Container>
  );
};

export default OrderDetails;