import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Form, Button, Card, Alert } from 'react-bootstrap';
import createAxiosInstance from '../utils/axios';

const Withdrawal = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [paymentData, setPaymentData] = useState('');
  const [error, setError] = useState(null);
  const [currencies, setCurrencies] = useState([]);
  const [selectedCurrency, setSelectedCurrency] = useState(null);

  useEffect(() => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.get('/get_currencies/')
      .then(response => {
        setCurrencies(response.data);
      })
      .catch(error => {
        console.log('Error fetching currencies: ' + error);
        setError('Error fetching currencies. Please try again.');
      });
  }, []);

  useEffect(() => {
    if (currencies.length > 0) {
      const currency = currencies.find(currency => currency.currency_id === parseInt(id));
      if (currency) {
        setSelectedCurrency(currency);
      }
    }
  }, [currencies, id]);

  const handleWithdrawal = () => {
    setError(null);
    const data = {
      currency: id,
      amount: amount,
      payment_data: paymentData
    };
    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/create_withdrawal/', data)
      .then(response => {
        if (response.data.msg === 'success') {
          navigate('/wallet');
        } else {
          setError('Withdrawal failed. Please try again.');
        }
      })
      .catch(error => {
        console.log('Error making withdrawal: ' + error);
        setError('Error making withdrawal. Please try again.');
      });
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title className="text-center">
                Withdrawal {selectedCurrency ? selectedCurrency.code : ''}
              </Card.Title>
              <Form>
                <Form.Group controlId="formAmount">
                  <Form.Label>Amount</Form.Label>
                  <Form.Control
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="Enter amount"
                    required
                  />
                </Form.Group>
                <Form.Group controlId="formPaymentData">
                  <Form.Label>Wallet Address</Form.Label>
                  <Form.Control
                    type="text"
                    value={paymentData}
                    onChange={(e) => setPaymentData(e.target.value)}
                    placeholder="Enter wallet address"
                    required
                  />
                </Form.Group>
                {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
                <Button variant="primary" onClick={handleWithdrawal} className="w-100 mt-3">
                  Withdrawal
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Withdrawal;