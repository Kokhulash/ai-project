# Task & Project Management API - API Reference Manual
**Version:** `1.0.0`  
**Base URL:** `http://localhost:8000`

API for managing projects, tasks, team assignments, and statuses.

## Table of Contents
- [POST `/projects`](#post-projects)
- [GET `/projects`](#get-projects)
- [GET `/projects/{project_id}`](#get-projectsproject_id)
- [DELETE `/projects/{project_id}`](#delete-projectsproject_id)
- [POST `/tasks`](#post-tasks)
- [GET `/tasks`](#get-tasks)
- [GET `/tasks/{task_id}`](#get-taskstask_id)
- [DELETE `/tasks/{task_id}`](#delete-taskstask_id)
- [PUT `/tasks/{task_id}`](#put-taskstask_id)

---

### <a id="post-projects"></a>POST `/projects`
**Summary:** Create a new project  
**Description:** Creates a project workspace  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/ProjectCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/ProjectResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/projects" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-projects"></a>GET `/projects`
**Summary:** List all projects  
**Description:** Retrieves paginated list of projects  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of records to return |
| `offset` | `query` | `False` | `integer` | Number of records to skip for pagination |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProjectListResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/projects" -H "Authorization: Bearer <TOKEN>"
```

### <a id="get-projectsproject_id"></a>GET `/projects/{project_id}`
**Summary:** Get project by ID  
**Description:** Fetches a project by its unique ID  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `project_id` | `path` | `True` | `string` | Unique identifier for project_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProjectResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/projects/{project_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="delete-projectsproject_id"></a>DELETE `/projects/{project_id}`
**Summary:** Delete project  
**Description:** Deletes project by ID  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `project_id` | `path` | `True` | `string` | Unique identifier for project_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/projects/{project_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-tasks"></a>POST `/tasks`
**Summary:** Create task  
**Description:** Creates a new task  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/TaskCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/TaskResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/tasks" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-tasks"></a>GET `/tasks`
**Summary:** List tasks  
**Description:** Retrieves tasks  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of records to return |
| `offset` | `query` | `False` | `integer` | Number of records to skip for pagination |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/TaskListResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/tasks" -H "Authorization: Bearer <TOKEN>"
```

### <a id="get-taskstask_id"></a>GET `/tasks/{task_id}`
**Summary:** Get task  
**Description:** Fetches task by ID  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `task_id` | `path` | `True` | `string` | Unique identifier for task_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/TaskResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/tasks/{task_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="delete-taskstask_id"></a>DELETE `/tasks/{task_id}`
**Summary:** Delete task  
**Description:** Deletes task by ID  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `task_id` | `path` | `True` | `string` | Unique identifier for task_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/tasks/{task_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="put-taskstask_id"></a>PUT `/tasks/{task_id}`
**Summary:** Update task  
**Description:** Updates task status  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `task_id` | `path` | `True` | `string` | Unique identifier for task_id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/TaskUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/TaskResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PUT "http://localhost:8000/tasks/{task_id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```
