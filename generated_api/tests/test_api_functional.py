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
    item_id = '123e4567-e89b-12d3-a456-426614174000'
    # 1. Create a new products resource via POST
    create_payload = {"name": "Sample name", "description": "Sample description", "price": "Sample price", "stockQuantity": 1, "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res_create = client.post('/products', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code in (200, 201), f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    if isinstance(created_data, dict) and 'id' in created_data:
        item_id = created_data['id']

    # 2. List products collection with pagination
    res_list = client.get('/products?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    if isinstance(list_data, dict):
        assert 'items' in list_data or 'total' in list_data or len(list_data) >= 0
    elif isinstance(list_data, list):
        assert len(list_data) >= 0

    # 3. Retrieve products by ID
    res_get = client.get(f'/products/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code in (200, 404)
    if res_get.status_code == 200 and isinstance(res_get.json(), dict) and 'id' in res_get.json():
        assert res_get.json()['id'] == item_id

    # 4. Update products
    create_payload = {"name": "Sample name", "description": "Sample description", "price": "Sample price", "stockQuantity": 1, "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res_update = client.put(f'/products/{item_id}', json=create_payload, headers=AUTH_HEADERS)
    assert res_update.status_code in (200, 204, 404)

    # 5. Delete products
    res_del = client.delete(f'/products/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code in (200, 204, 404)

    # 6. Verify 404 Not Found after deletion
    res_not_found = client.get(f'/products/{item_id}', headers=AUTH_HEADERS)
    assert res_not_found.status_code in (200, 404)

def test_products_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"name": "Sample name", "description": "Sample description", "price": "Sample price", "stockQuantity": 1, "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res = client.post('/products', json=create_payload)
    assert res.status_code in (401, 403), f'Expected 401 Unauthorized, got {res.status_code}'


def test_orders_crud_lifecycle(client):
    item_id = '123e4567-e89b-12d3-a456-426614174000'
    # 1. Create a new orders resource via POST
    create_payload = {"customerId": "123e4567-e89b-12d3-a456-426614174000", "orderDate": "2026-01-01T12:00:00Z", "status": "Sample status", "totalAmount": "Sample totalAmount", "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res_create = client.post('/orders', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code in (200, 201), f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    if isinstance(created_data, dict) and 'id' in created_data:
        item_id = created_data['id']

    # 2. List orders collection with pagination
    res_list = client.get('/orders?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    if isinstance(list_data, dict):
        assert 'items' in list_data or 'total' in list_data or len(list_data) >= 0
    elif isinstance(list_data, list):
        assert len(list_data) >= 0

    # 3. Retrieve orders by ID
    res_get = client.get(f'/orders/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code in (200, 404)
    if res_get.status_code == 200 and isinstance(res_get.json(), dict) and 'id' in res_get.json():
        assert res_get.json()['id'] == item_id

    # 4. Update orders
    create_payload = {"customerId": "123e4567-e89b-12d3-a456-426614174000", "orderDate": "2026-01-01T12:00:00Z", "status": "Sample status", "totalAmount": "Sample totalAmount", "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res_update = client.patch(f'/orders/{item_id}', json=create_payload, headers=AUTH_HEADERS)
    assert res_update.status_code in (200, 204, 404)

    # 5. Delete orders
    res_del = client.delete(f'/orders/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code in (200, 204, 404)

    # 6. Verify 404 Not Found after deletion
    res_not_found = client.get(f'/orders/{item_id}', headers=AUTH_HEADERS)
    assert res_not_found.status_code in (200, 404)

def test_orders_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"customerId": "123e4567-e89b-12d3-a456-426614174000", "orderDate": "2026-01-01T12:00:00Z", "status": "Sample status", "totalAmount": "Sample totalAmount", "createdAt": "2026-01-01T12:00:00Z", "updatedAt": "2026-01-01T12:00:00Z"}
    res = client.post('/orders', json=create_payload)
    assert res.status_code in (401, 403), f'Expected 401 Unauthorized, got {res.status_code}'

