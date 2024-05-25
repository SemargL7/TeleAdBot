import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Table, Button } from 'react-bootstrap';
import createAxiosInstance from '../utils/axios';

const Wallet = () => {
  const [balances, setBalances] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const axiosInstance = createAxiosInstance();
    axiosInstance.get('/get_balances/')
      .then(response => {
        setBalances(response.data);
      })
      .catch(error => {
        console.log('Error fetching data: ' + error);
      });
  }, []);

  const handleDeposit = (id) => {
    navigate(`/deposit/${id}`);
  };

  const handleWithdrawal = (id) => {
    navigate(`/withdrawal/${id}`);
  };

  return (
    <Container>
      <h1 className="my-4">Wallet</h1>
      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>Currency</th>
            <th>Total Balance</th>
            <th>Available</th>
            <th>Frozen Balance</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {balances.map(balance => (
            <tr key={balance.id}>
              <td>{balance.currency.code}</td>
              <td>{parseFloat(balance.balance) + parseFloat(balance.frozen_balance)}</td>
              <td>{balance.balance}</td>
              <td>{balance.frozen_balance}</td>
              <td>
                <Button
                  variant="success"
                  className="mr-2"
                  onClick={() => handleDeposit(balance.id)}
                >
                  Deposit
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleWithdrawal(balance.id)}
                >
                  Withdrawal
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default Wallet;