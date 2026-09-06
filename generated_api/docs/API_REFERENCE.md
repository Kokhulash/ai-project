# Book Management API - API Reference Manual
**Version:** `1.0.0`  
**Base URL:** `https://api.book-management.com/v1`

API for managing a collection of books, allowing for creation, retrieval, updating, and deletion of book records. It supports tracking book details like title, author, ISBN, publication year, genre, and copy availability.

## Table of Contents
- [POST `/books`](#post-books)
- [GET `/books`](#get-books)
- [GET `/books/{book_id}`](#get-booksbook_id)
- [PUT `/books/{book_id}`](#put-booksbook_id)
- [PATCH `/books/{book_id}`](#patch-booksbook_id)
- [DELETE `/books/{book_id}`](#delete-booksbook_id)

---

### <a id="post-books"></a>POST `/books`
**Summary:** Create a new book record  
**Description:** Adds a new book entry to the management system. The 'availableCopies' field will be automatically initialized to 'totalCopies' upon creation. The 'isbn' must be unique.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/BookCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Book created successfully | `#/components/schemas/Book` |
| `400` | Invalid request payload or data | `#/components/schemas/ErrorResponse` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity (e.g., unique ISBN violation, invalid publication year) | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/books" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-books"></a>GET `/books`
**Summary:** Retrieve a list of all books  
**Description:** Returns a collection of all books currently stored in the system. Supports optional pagination parameters.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of books to return |
| `offset` | `query` | `False` | `integer` | Number of books to skip before starting to collect the result set |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | A paginated list of books | `#/components/schemas/BookListResponse` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/books" -H "Authorization: Bearer <TOKEN>"
```

### <a id="get-booksbook_id"></a>GET `/books/{book_id}`
**Summary:** Retrieve a single book by ID  
**Description:** Returns the detailed information for a specific book identified by its unique ID.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier for book_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book details retrieved successfully | `#/components/schemas/Book` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |
| `404` | Book not found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="put-booksbook_id"></a>PUT `/books/{book_id}`
**Summary:** Update an existing book's details (full replacement)  
**Description:** Replaces all updatable fields of an existing book with the provided data. All fields (excluding 'id') must be provided in the request body. Note: 'isbn' must remain unique or be updated to a new unique value. 'availableCopies' cannot exceed 'totalCopies'.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier for book_id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/BookUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book updated successfully | `#/components/schemas/Book` |
| `400` | Invalid request payload or data | `#/components/schemas/ErrorResponse` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |
| `404` | Book not found | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity (e.g., unique ISBN violation, invalid publication year, availableCopies > totalCopies) | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PUT "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="patch-booksbook_id"></a>PATCH `/books/{book_id}`
**Summary:** Partially update an existing book's details  
**Description:** Updates specific fields of an existing book without requiring all fields. Only the fields provided in the request body will be modified. Note: 'isbn' must remain unique or be updated to a new unique value. 'availableCopies' cannot exceed 'totalCopies'.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier for book_id |

#### Request Body (`application/json`):
Ref: `#/components/schemas/BookPartialUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book updated successfully | `#/components/schemas/Book` |
| `400` | Invalid request payload or data | `#/components/schemas/ErrorResponse` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |
| `404` | Book not found | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity (e.g., unique ISBN violation, invalid publication year, availableCopies > totalCopies) | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PATCH "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="delete-booksbook_id"></a>DELETE `/books/{book_id}`
**Summary:** Delete a book record  
**Description:** Removes a book entry from the management system permanently.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier for book_id |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `401` | Authentication required or invalid credentials | `#/components/schemas/ErrorResponse` |
| `404` | Book not found | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>"
```
