# Book Library API - API Reference Manual
**Version:** `1.0.0`  
**Base URL:** `/api/v1`

API for managing books and facilitating the borrowing and returning of books by users in a library system. It allows users to browse available books, borrow them, and return them, while also providing administrative functions for managing the book catalog.

## Table of Contents
- [GET `/books`](#get-books)
- [POST `/books`](#post-books)
- [GET `/books/{book_id}`](#get-booksbook_id)
- [PUT `/books/{book_id}`](#put-booksbook_id)
- [DELETE `/books/{book_id}`](#delete-booksbook_id)
- [POST `/users`](#post-users)
- [GET `/users/{user_id}`](#get-usersuser_id)
- [GET `/borrowings`](#get-borrowings)
- [POST `/borrowings`](#post-borrowings)
- [GET `/borrowings/{borrowing_id}`](#get-borrowingsborrowing_id)
- [PATCH `/borrowings/{borrowing_id}/return`](#patch-borrowingsborrowing_idreturn)

---

### <a id="get-books"></a>GET `/books`
**Summary:** Retrieve a list of all books  
**Description:** Returns a paginated list of all books available in the library. Can be filtered by title, author, or genre, and sorted. Rule 1: A book can only be borrowed if its 'availableCopies' is greater than 0.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of items to return. |
| `offset` | `query` | `False` | `integer` | Number of items to skip before starting to collect the result set. |
| `title` | `query` | `False` | `string` | Filter books by title (partial match). |
| `author` | `query` | `False` | `string` | Filter books by author (partial match). |
| `genre` | `query` | `False` | `string` | Filter books by genre. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | A paginated list of books. | `#/components/schemas/BookListResponse` |
| `400` | Invalid query parameters. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/books" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-books"></a>POST `/books`
**Summary:** Add a new book to the library catalog  
**Description:** Allows library staff to add a new book entry to the system. Initial 'availableCopies' will be set to 'totalCopies'. Rule 7: Only library staff or administrators are authorized to add, update, or delete books. Rule 8: The 'isbn' field must be unique across all books in the library. Rule 10: Upon adding a new book, 'availableCopies' must be initialized to 'totalCopies'.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/BookCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Book successfully created. | `#/components/schemas/Book` |
| `400` | Invalid book data provided. | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/books" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-booksbook_id"></a>GET `/books/{book_id}`
**Summary:** Retrieve a specific book by ID  
**Description:** Returns the details of a single book identified by its unique ID.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier of the book. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book details. | `#/components/schemas/Book` |
| `400` | Invalid book ID format. | `#/components/schemas/ErrorResponse` |
| `404` | Book not found. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="put-booksbook_id"></a>PUT `/books/{book_id}`
**Summary:** Update an existing book's details  
**Description:** Allows library staff to fully update the details of an existing book. Requires all fields to be provided (excluding system-managed fields like 'availableCopies'). Rule 7: Only library staff or administrators are authorized to add, update, or delete books. Rule 8: The 'isbn' field must be unique across all books in the library.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier of the book to update. |

#### Request Body (`application/json`):
Ref: `#/components/schemas/BookUpdate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book successfully updated. | `#/components/schemas/Book` |
| `400` | Invalid book data provided. | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | Book not found. | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PUT "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="delete-booksbook_id"></a>DELETE `/books/{book_id}`
**Summary:** Remove a book from the library catalog  
**Description:** Allows library staff to remove a book from the system. This operation might be restricted if there are active borrowings for the book. Rule 7: Only library staff or administrators are authorized to add, update, or delete books.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book_id` | `path` | `True` | `string` | Unique identifier of the book to delete. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `204` | Resource deleted successfully | `None` |
| `400` | Invalid book ID format or book cannot be deleted due to active borrowings. | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | Book not found. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X DELETE "http://localhost:8000/books/{book_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-users"></a>POST `/users`
**Summary:** Register a new user  
**Description:** Allows a new user to register for a library account. Rule 9: The 'username' and 'email' fields must be unique for each user.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/UserCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | User successfully registered. | `#/components/schemas/User` |
| `400` | Invalid user data provided (e.g., duplicate username/email). | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized Access | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/users" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-usersuser_id"></a>GET `/users/{user_id}`
**Summary:** Retrieve a specific user's profile  
**Description:** Returns the profile details of a user. A user can retrieve their own profile, and administrators can retrieve any user's profile.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `path` | `True` | `string` | Unique identifier of the user. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | User profile details. | `#/components/schemas/User` |
| `400` | Invalid user ID format. | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | User not found. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/users/{user_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="get-borrowings"></a>GET `/borrowings`
**Summary:** Retrieve a list of borrowing records  
**Description:** Returns a list of borrowing records. For regular users, this lists their own borrowings. For administrators, it lists all borrowings. Can be filtered by user, book, or status.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `limit` | `query` | `False` | `integer` | Maximum number of items to return. |
| `offset` | `query` | `False` | `integer` | Number of items to skip before starting to collect the result set. |
| `userId` | `query` | `False` | `string` | Filter borrowings by user ID (admin only). |
| `bookId` | `query` | `False` | `string` | Filter borrowings by book ID. |
| `status` | `query` | `False` | `string` | Filter borrowings by status. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | A paginated list of borrowing records. | `#/components/schemas/BorrowingListResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/borrowings" -H "Authorization: Bearer <TOKEN>"
```

### <a id="post-borrowings"></a>POST `/borrowings`
**Summary:** Borrow a book  
**Description:** Allows an authenticated user to borrow an available book. The 'userId' is derived from the authentication token. Rule 1: A book can only be borrowed if its 'availableCopies' is greater than 0. Rule 2: When a book is borrowed, the 'availableCopies' for that book must decrease by 1. Rule 4: A user cannot have multiple active (not returned) borrowing records for the same book (identified by 'bookId'). Rule 5: The 'dueDate' for a borrowing is automatically calculated (e.g., 14 days from 'borrowDate'). Rule 6: Only authenticated users can borrow or return books.  
🔒 **Authentication Required:** Bearer Token

#### Request Body (`application/json`):
Ref: `#/components/schemas/BorrowingCreate`

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `201` | Book successfully borrowed. | `#/components/schemas/Borrowing` |
| `400` | Invalid request (e.g., book not available, already borrowed). | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | Book not found. | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/borrowings" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```

### <a id="get-borrowingsborrowing_id"></a>GET `/borrowings/{borrowing_id}`
**Summary:** Retrieve a specific borrowing record  
**Description:** Returns the details of a single borrowing record identified by its unique ID. Users can only access their own records.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `borrowing_id` | `path` | `True` | `string` | Unique identifier of the borrowing record. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Borrowing record details. | `#/components/schemas/Borrowing` |
| `400` | Invalid borrowing ID format. | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | Borrowing record not found or not accessible by user. | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X GET "http://localhost:8000/borrowings/{borrowing_id}" -H "Authorization: Bearer <TOKEN>"
```

### <a id="patch-borrowingsborrowing_idreturn"></a>PATCH `/borrowings/{borrowing_id}/return`
**Summary:** Return a borrowed book  
**Description:** Allows an authenticated user to mark a previously borrowed book as returned. Updates the borrowing record and book availability. Rule 3: When a book is returned, the 'availableCopies' for that book must increase by 1. Rule 6: Only authenticated users can borrow or return books.  
🔒 **Authentication Required:** Bearer Token

#### Parameters:
| Name | In | Required | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `borrowing_id` | `path` | `True` | `string` | Unique identifier of the borrowing record to mark as returned. |

#### Responses:
| Status Code | Description | Schema |
| :--- | :--- | :--- |
| `200` | Book successfully returned. | `#/components/schemas/Borrowing` |
| `400` | Invalid request (e.g., book already returned, not due for return). | `#/components/schemas/ErrorResponse` |
| `401` | Unauthorized. Authentication token is missing or invalid. | `#/components/schemas/ErrorResponse` |
| `404` | Borrowing record not found or not associated with the authenticated user. | `#/components/schemas/ErrorResponse` |
| `422` | Unprocessable Entity | `#/components/schemas/ErrorResponse` |

#### Example cURL:
```bash
curl -X PATCH "http://localhost:8000/borrowings/{borrowing_id}/return" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{}'
```
