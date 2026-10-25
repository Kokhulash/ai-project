# Auto-generated Pytest functional test suite by APIForge AI
import pytest
import httpx

BASE_URL = 'http://localhost:8000'
AUTH_HEADERS = {'Authorization': 'Bearer test-jwt-token'}

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'healthy'

def test_products_crud_lifecycle(client):
    # 1. Create a new products resource via POST
    create_payload = {"title": "Test title", "price": "Test price", "stock": 10}
    res_create = client.post('/products', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List products collection with pagination
    res_list = client.get('/products?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve products by ID
    res_get = client.get(f'/products/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

def test_products_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"title": "Test title", "price": "Test price", "stock": 10}
    res = client.post('/products', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'

def test_orders_crud_lifecycle(client):
    # 1. Create a new orders resource via POST
    create_payload = {"customer_id": "Test customer_id", "total_amount": "Test total_amount", "status": "Test status"}
    res_create = client.post('/orders', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List orders collection with pagination
    res_list = client.get('/orders?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve orders by ID
    res_get = client.get(f'/orders/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

def test_orders_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"customer_id": "Test customer_id", "total_amount": "Test total_amount", "status": "Test status"}
    res = client.post('/orders', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'
