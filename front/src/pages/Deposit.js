import React, { useEffect, useState } from 'react';
import {Link, useParams} from 'react-router-dom';
import { Container, Row, Col, Form, Button, Card, Alert } from 'react-bootstrap';
import createAxiosInstance from '../utils/axios';

const Deposit = () => {
  const { id } = useParams();
  const [amount, setAmount] = useState('');
  const [depositAddress, setDepositAddress] = useState('');
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


  const handleDeposit = () => {
    setError(null);
    const data = {
      currency: id,
      amount: amount
    };
    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/create_deposit/', data)
      .then(response => {
        if (response.data.msg === 'success') {
          setDepositAddress(response.data.data);
        } else {
          setError('Deposit failed. Please try again.');
        }
      })
      .catch(error => {
        console.log('Error making deposit: ' + error);
        setError('Error making deposit. Please try again.');
      });
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title className="text-center">
                Deposit {selectedCurrency ? selectedCurrency.code : ''}
              </Card.Title>
              {depositAddress ? (
                <Alert variant="success">
                  <p>Send your deposit to the following address:</p>
                  <strong>{depositAddress}</strong>
                  <p>Amount: {amount} {selectedCurrency ? selectedCurrency.code : ''}</p>
                  <Link to="/wallet" className="btn btn-primary">Back to Wallet</Link>
                </Alert>
              ) : (
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
                  {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
                  <Button variant="primary" onClick={handleDeposit} className="w-100 mt-3">
                    Deposit
                  </Button>
                </Form>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Deposit;