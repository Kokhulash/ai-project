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

def test_books_crud_lifecycle(client):
    # 1. Create a new books resource via POST
    create_payload = {"title": "Test title", "author": "Test author", "isbn": "Test isbn", "publicationYear": 10, "genre": "Test genre", "totalCopies": 10}
    res_create = client.post('/books', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List books collection with pagination
    res_list = client.get('/books?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve books by ID
    res_get = client.get(f'/books/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

    # 4. Update books
    res_update = client.put(f'/books/{item_id}', json=create_payload, headers=AUTH_HEADERS)
    assert res_update.status_code in (200, 204)

    # 5. Delete books
    res_del = client.delete(f'/books/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code == 204

    # 6. Verify 404 Not Found after deletion
    res_not_found = client.get(f'/books/{item_id}', headers=AUTH_HEADERS)
    assert res_not_found.status_code == 404

def test_books_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"title": "Test title", "author": "Test author", "isbn": "Test isbn", "publicationYear": 10, "genre": "Test genre", "totalCopies": 10}
    res = client.post('/books', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'

def test_users_crud_lifecycle(client):
    # 1. Create a new users resource via POST
    create_payload = {"username": "Test username", "email": "Test email", "firstName": "Test firstName", "lastName": "Test lastName"}
    res_create = client.post('/users', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 3. Retrieve users by ID
    res_get = client.get(f'/users/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

def test_users_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"username": "Test username", "email": "Test email", "firstName": "Test firstName", "lastName": "Test lastName"}
    res = client.post('/users', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'

def test_borrowings_crud_lifecycle(client):
    # 1. Create a new borrowings resource via POST
    create_payload = {"bookId": "Test bookId"}
    res_create = client.post('/borrowings', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List borrowings collection with pagination
    res_list = client.get('/borrowings?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve borrowings by ID
    res_get = client.get(f'/borrowings/{item_id}/return', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

    # 4. Update borrowings
    res_update = client.patch(f'/borrowings/{item_id}/return', json=create_payload, headers=AUTH_HEADERS)
    assert res_update.status_code in (200, 204)

def test_borrowings_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"bookId": "Test bookId"}
    res = client.post('/borrowings', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'
