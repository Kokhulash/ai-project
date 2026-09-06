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

def test_projects_crud_lifecycle(client):
    # 1. Create a new projects resource via POST
    create_payload = {"name": "Test name", "description": "Test description"}
    res_create = client.post('/projects', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List projects collection with pagination
    res_list = client.get('/projects?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve projects by ID
    res_get = client.get(f'/projects/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

    # 5. Delete projects
    res_del = client.delete(f'/projects/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code == 204

    # 6. Verify 404 Not Found after deletion
    res_not_found = client.get(f'/projects/{item_id}', headers=AUTH_HEADERS)
    assert res_not_found.status_code == 404

def test_projects_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"name": "Test name", "description": "Test description"}
    res = client.post('/projects', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'

def test_tasks_crud_lifecycle(client):
    # 1. Create a new tasks resource via POST
    create_payload = {"project_id": "Test project_id", "title": "Test title", "status": "Test status", "assigned_to": "Test assigned_to"}
    res_create = client.post('/tasks', json=create_payload, headers=AUTH_HEADERS)
    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'
    created_data = res_create.json()
    assert 'id' in created_data, 'Created item must have an id'
    item_id = created_data['id']

    # 2. List tasks collection with pagination
    res_list = client.get('/tasks?limit=10&offset=0', headers=AUTH_HEADERS)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert 'items' in list_data
    assert len(list_data['items']) >= 1

    # 3. Retrieve tasks by ID
    res_get = client.get(f'/tasks/{item_id}', headers=AUTH_HEADERS)
    assert res_get.status_code == 200
    assert res_get.json()['id'] == item_id

    # 4. Update tasks
    res_update = client.put(f'/tasks/{item_id}', json=create_payload, headers=AUTH_HEADERS)
    assert res_update.status_code in (200, 204)

    # 5. Delete tasks
    res_del = client.delete(f'/tasks/{item_id}', headers=AUTH_HEADERS)
    assert res_del.status_code == 204

    # 6. Verify 404 Not Found after deletion
    res_not_found = client.get(f'/tasks/{item_id}', headers=AUTH_HEADERS)
    assert res_not_found.status_code == 404

def test_tasks_auth_required(client):
    # Accessing secured endpoint without token should return 401
    create_payload = {"project_id": "Test project_id", "title": "Test title", "status": "Test status", "assigned_to": "Test assigned_to"}
    res = client.post('/tasks', json=create_payload)
    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'
