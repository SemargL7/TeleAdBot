import React, { useState, useEffect } from 'react';
import createAxiosInstance from "../utils/axios";
import { Form, Button, Container, Row, Col, Card } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const CreateAd = () => {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState('');
  const [options, setOptions] = useState([{ advertisement_option_type: '', price: '', currency: '' }]);
  const [currencies, setCurrencies] = useState([]);
  const [description, setDescription] = useState("");
  const [optionsTypes, setOptionsTypes] = useState([]);
  const axios = createAxiosInstance();
  const navigate = useNavigate();


  useEffect(() => {

    axios.get('/get_my_chats/').then((response) => {
      setChats(response.data);
    });


    axios.get('/get_currencies/').then((response) => {
      setCurrencies(response.data);
    });


    axios.get('/get_all_ad_options_types/').then((response) => {
      setOptionsTypes(response.data);
    });
  }, []);

  const handleChatChange = (e) => {
    setSelectedChat(e.target.value);
  };

  const handleOptionChange = (index, e) => {
    const updatedOptions = options.map((option, i) =>
      i === index ? { ...option, [e.target.name]: e.target.value } : option
    );
    setOptions(updatedOptions);
  };

  const handleAddOption = () => {
    setOptions([...options, { advertisement_option_type: '', price: '', currency: '' }]);
  };

  const handleRemoveOption = (index) => {
    const updatedOptions = options.filter((_, i) => i !== index);
    setOptions(updatedOptions);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const adData = {
      chat: selectedChat,
      options: options,
      description: description
    };


    axios.post('/create_advertisement/', adData)
      .then((response) => {
        console.log('Advertisement created:', response.data);
        navigate('/myAds');
      })
      .catch((error) => {
        console.error('There was an error creating the advertisement!', error);
      });
  };

  return (
    <Container className="mt-5">
      <h1 className="mb-4">Create Advertisement</h1>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Chat</Form.Label>
          <Form.Control as="select" value={selectedChat} onChange={handleChatChange} required>
            <option value="">Select a chat</option>
            {chats.map((chat) => (
              <option key={chat.chat_id} value={chat.chat_id}>
                {chat.title}
              </option>
            ))}
          </Form.Control>
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Description</Form.Label>
          <Form.Control as="textarea" value={description} onChange={(e) => setDescription(e.target.value)} required />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Options</Form.Label>
          {options.map((option, index) => (
            <Card key={index} className="mb-3">
              <Card.Body>
                <Row>
                  <Col md={4}>
                    <Form.Group>
                      <Form.Label>Option Type</Form.Label>
                      <Form.Control
                        as="select"
                        name="advertisement_option_type"
                        value={option.advertisement_option_type}
                        onChange={(e) => handleOptionChange(index, e)}
                        required
                      >
                        <option value="">Select an option type</option>
                        {optionsTypes.map((optType) => (
                          <option key={optType.advertisement_option_type} value={optType.advertisement_option_type}>
                            {optType.advertisement_option_type_name}
                          </option>
                        ))}
                      </Form.Control>
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group>
                      <Form.Label>Price</Form.Label>
                      <Form.Control
                        type="number"
                        name="price"
                        placeholder="Price"
                        value={option.price}
                        onChange={(e) => handleOptionChange(index, e)}
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group>
                      <Form.Label>Currency</Form.Label>
                      <Form.Control
                        as="select"
                        name="currency"
                        value={option.currency}
                        onChange={(e) => handleOptionChange(index, e)}
                        required
                      >
                        <option value="">Select a currency</option>
                        {currencies.map((currency) => (
                          <option key={currency.currency_id} value={currency.currency_id}>
                            {currency.name}
                          </option>
                        ))}
                      </Form.Control>
                    </Form.Group>
                  </Col>
                </Row>
                <Button variant="danger" onClick={() => handleRemoveOption(index)} className="mt-3">Remove Option</Button>
              </Card.Body>
            </Card>
          ))}
          <Button variant="secondary" onClick={handleAddOption}>Add Option</Button>
        </Form.Group>

        <Button variant="primary" type="submit">Create Advertisement</Button>
      </Form>
    </Container>
  );
};

export default CreateAd;