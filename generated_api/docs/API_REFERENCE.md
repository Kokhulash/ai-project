# E-Commerce Product and Order Management API - API Reference Manual
**Version:** `1.0.0`  
**Base URL:** `http://localhost:8000`

API for managing products available for sale and customer orders within an e-commerce system. It supports product catalog management, including creation, retrieval, update, and deletion of products, as well as the full lifecycle of customer orders, from creation to status updates and cancellation.

## Table of Contents
- [GET `/products`](#get-products)
- [POST `/products`](#post-products)
- [GET `/products/{id}`](#get-productsid)
- [PUT `/products/{id}`](#put-productsid)
- [PATCH `/products/{id}`](#patch-productsid)
- [DELETE `/products/{id}`](#delete-productsid)
- [GET `/orders`](#get-orders)
- [POST `/orders`](#post-orders)
- [GET `/orders/{id}`](#get-ordersid)
- [PATCH `/orders/{id}`](#patch-ordersid)
- [DELETE `/orders/{id}`](#delete-ordersid)

---

### <a id="get-products"></a>GET `/products`
**Summary:** Retrieve a list of all products  
**Description:** Returns a paginated list of all available products in the catalog. Supports filtering and sorting.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of records to return |
| `offset` | `query` | `False` | `integer` | Number of records to skip for pagination |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProductListResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/products" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-products"></a>POST `/products`
**Summary:** Create a new product  
**Description:** Adds a new product to the catalog. Requires product details such as name, description, price, and initial stock quantity. Only authorized users can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/ProductCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/ProductResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/products" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-productsid"></a>GET `/products/{id}`
**Summary:** Retrieve a single product by ID  
**Description:** Returns the details of a specific product identified by its unique ID.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProductResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/products/{id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="put-productsid"></a>PUT `/products/{id}`
**Summary:** Update an existing product  
**Description:** Updates all details of an existing product identified by its ID. All fields in the request body are required for a full replacement. Only authorized users can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/ProductUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProductResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PUT "http://localhost:8000/products/{id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="patch-productsid"></a>PATCH `/products/{id}`
**Summary:** Partially update an existing product  
**Description:** Updates specific fields of an existing product identified by its ID. Only the fields provided in the request body will be updated. Only authorized users can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/ProductUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/ProductResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PATCH "http://localhost:8000/products/{id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="delete-productsid"></a>DELETE `/products/{id}`
**Summary:** Delete a product  
**Description:** Removes a product from the catalog. This operation might be restricted if the product is part of existing orders. Only authorized users can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/products/{id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="get-orders"></a>GET `/orders`
**Summary:** Retrieve a list of all orders  
**Description:** Returns a paginated list of all customer orders. Can be filtered by customer ID or status. Only authorized users (e.g., admins) can view all orders; customers can only view their own.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of records to return |
| `offset` | `query` | `False` | `integer` | Number of records to skip for pagination |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/OrderListResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/orders" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-orders"></a>POST `/orders`
**Summary:** Create a new order  
**Description:** Creates a new customer order with specified products and quantities. This operation validates product availability, decrements stock quantities, and calculates the total amount.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/OrderCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Resource created successfully | `#/components/schemas/OrderResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/orders" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-ordersid"></a>GET `/orders/{id}`
**Summary:** Retrieve a single order by ID  
**Description:** Returns the details of a specific order, including its line items. Access is restricted to the order's customer or authorized personnel.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/OrderResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/orders/{id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="patch-ordersid"></a>PATCH `/orders/{id}`
**Summary:** Update an order's status  
**Description:** Allows updating the status of an existing order (e.g., from 'pending' to 'shipped' or 'delivered'). This operation might trigger further business logic like stock replenishment if cancelled. Only authorized users can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/OrderStatusUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Successful operation | `#/components/schemas/OrderResponse` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PATCH "http://localhost:8000/orders/{id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="delete-ordersid"></a>DELETE `/orders/{id}`
**Summary:** Cancel an order  
**Description:** Marks an order as 'cancelled'. This operation should trigger stock replenishment for the items in the order, provided the order has not been shipped or delivered. Only authorized users or the customer (within a certain timeframe) can perform this action.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `path` | `True` | `string` | Unique identifier for id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Bad Request / Validation Failure | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized / Missing Token | `#/components/schemas/ErrorResponse` |
| `404` | Resource Not Found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/orders/{id}" -H "Authorization: Bearer <TOKEN>"
```
