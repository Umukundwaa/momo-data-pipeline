# MoMo Data Pipeline — API Documentation
## Authentication

All endpoints require Basic Authentication. Include credentials in every request:

```bash
curl http://localhost:8000/transactions -u your username here: your password here

```

If credentials are missing or wrong, the API returns:

```json
HTTP/1.1 401 Unauthorized

{
  "error": "Unauthorized",
  "message": "Invalid or missing credentials. Use Basic Auth with username and password."
}
```

---

## Endpoints

---

### 1. GET /transactions

Returns a list of transactions. Defaults to first 50.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Number of transactions to return (default: 50) |
| `type` | string | Filter by transaction type e.g. `Incoming Money` |

**Request:**

```bash
curl http://localhost:8000/transactions -u your username here: your password here
curl "http://localhost:8000/transactions?limit=10&type=Incoming%20Money" -u your username here: your password here

```

**Response (200 OK):**

```json
{
  "total": 1691,
  "showing": 50,
  "transactions": [
    {
      "id": 1,
      "transaction_id": "76662021700",
      "type": "Incoming Money",
      "amount": 2000.0,
      "fee": 0.0,
      "sender": "Jane Smith",
      "receiver": null,
      "new_balance": 2000.0,
      "date": "10 May 2024 4:30:58 PM",
      "timestamp_ms": 1715351458724,
      "raw_body": "You have received 2000 RWF from Jane Smith..."
    }
  ]
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized — wrong or missing credentials |

---

### 2. GET /transactions/{id}

Returns a single transaction by its ID.

**Request:**

```bash
curl http://localhost:8000/transactions/1 -u your username here: your password here

```

**Response (200 OK):**

```json
{
  "id": 1,
  "transaction_id": "76662021700",
  "type": "Incoming Money",
  "amount": 2000.0,
  "fee": 0.0,
  "sender": "Jane Smith",
  "receiver": null,
  "new_balance": 2000.0,
  "date": "10 May 2024 4:30:58 PM",
  "timestamp_ms": 1715351458724,
  "raw_body": "You have received 2000 RWF from Jane Smith (*********013)..."
}
```

**Response (404 Not Found):**

```json
{
  "error": "Not Found",
  "message": "Transaction with ID 9999 does not exist."
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Transaction not found |

---

### 3. POST /transactions

Adds a new transaction record.

**Request Headers:**

```
Content-Type: application/json
Authorization: Basic YWRtaW46bmV4dXMxMjM=
```

**Request Body:**

```json
{
  "type": "Incoming Money",
  "amount": 15000,
  "fee": 0,
  "sender": "John Doe",
  "receiver": null,
  "new_balance": 20000,
  "date": "30 May 2026 10:00:00 AM",
  "transaction_id": "TXN999999999"
}
```

**Request:**

```bash
curl -X POST http://localhost:8000/transactions \
  -u your username here: your password here
 \
  -H "Content-Type: application/json" \
  -d '{"type":"Incoming Money","amount":15000,"sender":"John Doe","fee":0}'
```

**Response (201 Created):**

```json
{
  "message": "Transaction created successfully.",
  "transaction": {
    "id": 1692,
    "transaction_id": "TXN999999999",
    "type": "Incoming Money",
    "amount": 15000.0,
    "fee": 0.0,
    "sender": "John Doe",
    "receiver": null,
    "new_balance": 20000.0,
    "date": "30 May 2026 10:00:00 AM",
    "timestamp_ms": 0,
    "raw_body": ""
  }
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| 201 | Created successfully |
| 400 | Bad Request — missing required fields or invalid data |
| 401 | Unauthorized |

---

### 4. PUT /transactions/{id}

Updates an existing transaction record.

**Request:**

```bash
curl -X PUT http://localhost:8000/transactions/1 \
  -u your username here: your password here
 \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "fee": 100}'
```

**Response (200 OK):**

```json
{
  "message": "Transaction updated successfully.",
  "transaction": {
    "id": 1,
    "type": "Incoming Money",
    "amount": 5000.0,
    "fee": 100.0,
    "sender": "Jane Smith",
    ...
  }
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| 200 | Updated successfully |
| 400 | Bad Request — invalid data |
| 401 | Unauthorized |
| 404 | Transaction not found |

---

### 5. DELETE /transactions/{id}

Deletes a transaction record.

**Request:**

```bash
curl -X DELETE http://localhost:8000/transactions/1 -u your username here: your password here

```

**Response (200 OK):**

```json
{
  "message": "Transaction 1 deleted successfully."
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| 200 | Deleted successfully |
| 401 | Unauthorized |
| 404 | Transaction not found |

---

### 6. GET /health

Health check endpoint — verifies the API is running.

**Request:**

```bash
curl http://localhost:8000/health -u your username here: your password here

```

**Response (200 OK):**

```json
{
  "status": "ok",
  "total_transactions": 1691,
  "api": "MoMo Data Pipeline API",
  "team": "Team Nexus"
}
```

---

## Error Code Summary

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | New resource created successfully |
| 400 | Bad Request | Invalid or missing request data |
| 401 | Unauthorized | Missing or wrong credentials |
| 404 | Not Found | Resource or endpoint does not exist |

---

## Transaction Types

| Type | Description |
|------|-------------|
| `Incoming Money` | Money received from another user |
| `Payment to Code` | Payment made to a merchant code |
| `Transfer to Mobile` | Money sent to another phone number |
| `Bank Deposit` | Money deposited from a bank account |
| `Airtime Bill` | Airtime purchased using MoMo |
| `Other` | Does not match known patterns |

---

## Running the API

```bash
# Install dependencies (none required — plain Python)
python api/server.py

# Server starts at http://localhost:8000
# Credentials: your username here: your password here
```

---

## Security Notes

### Why Basic Auth is Weak

Basic Authentication encodes credentials in Base64 — **not encryption**. Anyone who intercepts the HTTP request can easily decode `YWRtaW46bmV4dXMxMjM=` back to `admin:nexus123`. It is vulnerable to:

- **Man-in-the-middle attacks** — credentials exposed if not using HTTPS
- **Credential theft** — credentials sent with every single request
- **No token expiry** — credentials never expire automatically
- **No granular permissions** — one password gives full access to everything

### Stronger Alternatives

| Method | Why It Is Better |
|--------|-----------------|
| **JWT (JSON Web Tokens)** | Token expires after set time, no credentials sent repeatedly, can include user roles and permissions |
| **OAuth2** | Industry standard, supports third-party login, granular scopes, used by Google and GitHub |
| **API Keys** | Per-client keys, easy to revoke one key without affecting others |
| **HTTPS + Basic Auth** | If Basic Auth must be used, always combine with HTTPS to encrypt the connection |
