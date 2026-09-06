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

def test_patients_crud_lifecycle(client):
    # 1. Create a new patients resource via POST
    create_payload = {"full_name": "Test full_name", "birth_date": "Test birth_date"}
    res_create = client.post('/patients', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List patients collection with pagination
    res_list = client.get('/patients?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve patients by ID
    res_get = client.get(f'/patients/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

def test_patients_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"full_name": "Test full_name", "birth_date": "Test birth_date"}
    res = client.post('/patients', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'

def test_appointments_crud_lifecycle(client):
    # 1. Create a new appointments resource via POST
    create_payload = {"patient_id": "Test patient_id", "appointment_time": "Test appointment_time", "status": "Test status"}
    res_create = client.post('/appointments', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 5. Delete appointments
    res_del = client.delete(f'/appointments/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code == 204

def test_appointments_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"patient_id": "Test patient_id", "appointment_time": "Test appointment_time", "status": "Test status"}
    res = client.post('/appointments', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'
