from flask import json
import pytest
from options_chain.routes import options_api

@pytest.fixture
def client():
    from options_chain_dashboard.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_options_chain(client):
    response = client.get('/api/options_chain')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Expecting a list of options data

def test_get_option_details(client):
    option_id = 1  # Assuming an option with ID 1 exists
    response = client.get(f'/api/options_chain/{option_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data and data['id'] == option_id

def test_invalid_option_id(client):
    response = client.get('/api/options_chain/9999')  # Assuming this ID does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data and data['error'] == 'Option not found'

def test_post_new_option(client):
    new_option = {
        "ticker": "AAPL",
        "strike_price": 150,
        "expiration_date": "2023-12-31",
        "option_type": "call",
        "premium": 5.00
    }
    response = client.post('/api/options_chain', json=new_option)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data  # Ensure an ID is returned for the new option

def test_post_invalid_option(client):
    invalid_option = {
        "ticker": "AAPL",
        "strike_price": "invalid",  # Invalid data type
        "expiration_date": "2023-12-31",
        "option_type": "call",
        "premium": 5.00
    }
    response = client.post('/api/options_chain', json=invalid_option)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data and data['error'] == 'Invalid input data'