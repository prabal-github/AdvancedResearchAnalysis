from options_chain import create_app
import pytest

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_options_dashboard_access(client):
    response = client.get('/options_chain/dashboard')
    assert response.status_code == 200
    assert b'Options Chain Dashboard' in response.data

def test_options_chain_data(client):
    response = client.get('/api/options_chain/data')
    assert response.status_code == 200
    assert 'options' in response.json

def test_options_chain_ml_features(client):
    response = client.get('/api/options_chain/ml_features')
    assert response.status_code == 200
    assert 'predictions' in response.json

def test_options_chain_dashboard_rendering(client):
    response = client.get('/options_chain/dashboard')
    assert response.status_code == 200
    assert b'Greeks Panel' in response.data
    assert b'Signals Panel' in response.data
    assert b'Charts' in response.data

def test_options_chain_dashboard_access_for_admin(client):
    # Simulate admin login if necessary
    response = client.get('/options_chain/dashboard?role=admin')
    assert response.status_code == 200
    assert b'Options Chain Dashboard' in response.data

def test_options_chain_dashboard_access_for_investor(client):
    # Simulate investor login if necessary
    response = client.get('/options_chain/dashboard?role=investor')
    assert response.status_code == 200
    assert b'Options Chain Dashboard' in response.data