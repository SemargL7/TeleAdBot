import React, { useState, useEffect } from 'react';
import createAxiosInstance from "../utils/axios";
import moment from 'moment-timezone';
import { Form, Button, Container, Row, Col, Card } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const CreateOrder = () => {
  const [adId, setAdId] = useState(null);
  const [ad, setAd] = useState(null);
  const [availableOptions, setAvailableOptions] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [optionData, setOptionData] = useState({});
  const [paymentTime, setPaymentTime] = useState('');
  const [timezone, setTimezone] = useState(moment.tz.guess());
  const navigate = useNavigate();


  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const adIdParam = urlParams.get('ad_id');
    if (adIdParam) {
      setAdId(adIdParam);
    }
  }, []);

  useEffect(() => {
    if (adId != null) {
      const axiosInstance = createAxiosInstance();
      axiosInstance.get(`/get_ad?ad_id=${adId}`)
        .then(response => {
          setAd(response.data);
          setAvailableOptions(response.data.options);
        })
        .catch(error => {
          console.log('Error fetching data: ' + error);
        });
    }
  }, [adId]);

  const handleAddOption = () => {
    setSelectedOptions([...selectedOptions, { optionId: null, schedule_time: '', post_data: { text: '', buttons: [] } }]);
  };

  const handleRemoveOption = (index) => {
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions.splice(index, 1);
    setSelectedOptions(newSelectedOptions);
  };

  const handleOptionSelect = (e, index) => {
    const optionId = parseInt(e.target.value);
    const selectedOption = availableOptions.find(option => option.id === optionId);
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[index] = {
      optionId,
      schedule_time: '',
      post_data: { text: '', buttons: [] }
    };
    setSelectedOptions(newSelectedOptions);
    setOptionData({
      ...optionData,
      [optionId]: {
        ...optionData[optionId],
        price: selectedOption.price,
        advertisement_option_type: selectedOption.advertisement_option_type
      }
    });
  };

  const handleScheduleTimeChange = (e, index) => {
    const value = e.target.value;
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[index].schedule_time = value;
    setSelectedOptions(newSelectedOptions);
  };

  const handlePostDataChange = (e, index, field) => {
    const value = e.target.value;
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[index].post_data[field] = value;
    setSelectedOptions(newSelectedOptions);
  };

  const handleAddButton = (index) => {
    const newButton = { text: '', url: '' };
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[index].post_data.buttons.push(newButton);
    setSelectedOptions(newSelectedOptions);
  };

  const handleRemoveButton = (optionIndex, buttonIndex) => {
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[optionIndex].post_data.buttons.splice(buttonIndex, 1);
    setSelectedOptions(newSelectedOptions);
  };

  const handleButtonChange = (e, index, buttonIndex, field) => {
    const value = e.target.value;
    const newSelectedOptions = [...selectedOptions];
    newSelectedOptions[index].post_data.buttons[buttonIndex][field] = value;
    setSelectedOptions(newSelectedOptions);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const orderData = {
      advertisement: adId,
      options: selectedOptions.map(option => ({
        advertisement_option: option.optionId,
        scheduledAt: moment.tz(option.schedule_time, timezone).format(),
        post_data: option.post_data
      })),
      payment_time: moment.tz(paymentTime, timezone).format()
    };

    const axiosInstance = createAxiosInstance();
    axiosInstance.post('/create_order/', orderData)
      .then(response => {
        console.log('Order created successfully:', response.data);
        navigate('/myOrders');
      })
      .catch(error => {
        console.error('Error creating order:', error);
      });
  };

  return (
    <Container className="mt-5">
      <h1 className="mb-4">Create Order for Advertisement</h1>
      {ad && (
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Advertisement</Form.Label>
            <Card>
              <Card.Body>
                <Card.Title>{ad.chat.title}</Card.Title>
                <Card.Text>
                  <strong>Type:</strong> {ad.chat.chat_type.chat_type_name}
                </Card.Text>
              </Card.Body>
            </Card>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Select Options</Form.Label>
            {selectedOptions.map((option, index) => (
              <Card key={index} className="mb-3">
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Option Type</Form.Label>
                        <Form.Control as="select" value={option.optionId || ''} onChange={(e) => handleOptionSelect(e, index)} required>
                          <option value="">Select an option</option>
                          {availableOptions.map(opt => (
                            <option key={opt.id} value={opt.id}>{opt.advertisement_option_type.advertisement_option_type_name} - ${opt.price}</option>
                          ))}
                        </Form.Control>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Schedule Time</Form.Label>
                        <Form.Control
                          type="datetime-local"
                          value={option.schedule_time}
                          onChange={(e) => handleScheduleTimeChange(e, index)}
                          required
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  {option.optionId && (
                    <>
                      <Row>
                        <Col md={8}>
                          <Form.Group>
                            <Form.Label>Post Data Text</Form.Label>
                            <Form.Control
                              type="text"
                              value={option.post_data.text}
                              onChange={(e) => handlePostDataChange(e, index, 'text')}
                              required
                            />
                          </Form.Group>
                        </Col>
                      </Row>
                      <Form.Group className="mt-3">
                        <Form.Label>Buttons</Form.Label>
                        {option.post_data.buttons.map((button, btnIndex) => (
                          <Row key={btnIndex} className="mb-2">
                            <Col>
                              <Form.Control
                                type="text"
                                placeholder="Button Text"
                                value={button.text}
                                onChange={(e) => handleButtonChange(e, index, btnIndex, 'text')}
                                required
                              />
                            </Col>
                            <Col>
                              <Form.Control
                                type="text"
                                placeholder="Button URL"
                                value={button.url}
                                onChange={(e) => handleButtonChange(e, index, btnIndex, 'url')}
                                required
                              />
                            </Col>
                            <Col md="auto">
                              <Button variant="danger" onClick={() => handleRemoveButton(index, btnIndex)}>Remove Button</Button>
                            </Col>
                          </Row>
                        ))}
                        <Button variant="secondary" onClick={() => handleAddButton(index)}>Add Button</Button>
                      </Form.Group>
                      <Button variant="danger" onClick={() => handleRemoveOption(index)} className="mt-3">Remove Option</Button>
                    </>
                  )}
                </Card.Body>
              </Card>
            ))}
            <Button variant="secondary" onClick={handleAddOption}>Add Option</Button>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Payment Time</Form.Label>
            <Form.Control
              type="datetime-local"
              value={paymentTime}
              onChange={(e) => setPaymentTime(e.target.value)}
              required
            />
          </Form.Group>

          <Button variant="primary" type="submit">Create Order</Button>
        </Form>
      )}
    </Container>
  );
};

export default CreateOrder;