# Healthcare Clinical API - API Reference Manual
**Version:** `1.0.0`  
**Base URL:** `http://localhost:8000`

API for patient health records and clinical appointments.

## Table of Contents
- [GET `/patients`](#get-patients)
- [POST `/patients`](#post-patients)
- [GET `/patients/{patient_id}`](#get-patientspatient_id)
- [POST `/appointments`](#post-appointments)
- [DELETE `/appointments/{appointment_id}`](#delete-appointmentsappointment_id)

---

### <a id="get-patients"></a>GET `/patients`
**Summary:** List patients  
**Description:** List patients  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of records to return |
| `offset` | `query` | `False` | `integer` | Number of records to skip for pagination |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/PatientListResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/patients" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-patients"></a>POST `/patients`
**Summary:** Register patient  
**Description:** Register patient  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/PatientCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/PatientResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/patients" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-patientspatient_id"></a>GET `/patients/{patient_id}`
**Summary:** Get patient  
**Description:** Get patient  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `patient_id` | `path` | `True` | `string` | Unique identifier for patient_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/PatientResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/patients/{patient_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-appointments"></a>POST `/appointments`
**Summary:** Schedule appointment  
**Description:** Schedule appointment  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/AppointmentCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/AppointmentResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/appointments" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="delete-appointmentsappointment_id"></a>DELETE `/appointments/{appointment_id}`
**Summary:** Cancel appointment  
**Description:** Cancel appointment  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `appointment_id` | `path` | `True` | `string` | Unique identifier for appointment_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/appointments/{appointment_id}" -H "Authorization: Bearer <TOKEN>"
```
