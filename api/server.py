import json
import base64
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path so we can import parse_xml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_xml import parse_xml

# CONFIGURATION
HOST = "localhost"
PORT = 8000

# Basic Auth credentials
VALID_USERNAME = os.getenv("API_USERNAME")
VALID_PASSWORD = os.getenv("API_PASSWORD")

# Load and store all transactions in memory
XML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../modified_sms_v2.xml")

print("Loading transactions from XML...")
ALL_TRANSACTIONS = parse_xml(XML_FILE)

# DSA TWO DATA STRUCTURES FOR FAST LOOKUP

# List  used for linear search
transactions_list = ALL_TRANSACTIONS

# dictionary lookup (id → transaction)
transactions_dict = {t["id"]: t for t in ALL_TRANSACTIONS}

print(f"Loaded {len(transactions_list)} transactions")
print(f"Dictionary index built with {len(transactions_dict)} entries")

# Authentication handler
def check_auth(handler):
    """ Check Basic Authentication header"""
    auth_header = handler.headers.get("Authorization", "")

    if not auth_header.startswith("Basic "):
        return False

    try:
        # Decode base64 credentials
        encoded = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username == VALID_USERNAME and password == VALID_PASSWORD
    except Exception:
        return False


def send_unauthorized(handler):
    """Send 401 Unauthorized response."""
    handler.send_response(401)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
    handler.end_headers()
    handler.wfile.write(json.dumps({
        "error": "Unauthorized",
        "message": "Invalid or missing credentials. Use Basic Auth with username and password."
    }).encode())


def send_json(handler, status, data):
    """Send a JSON response with given status code."""
    body = json.dumps(data, indent=2).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

# DSA LINEAR SEARCH

def linear_search(transaction_id):
    """
    Linear Search — O(n)
    Scans through the list one by one until ID is found.
    """
    for transaction in transactions_list:
        if transaction["id"] == transaction_id:
            return transaction
    return None

# DSA DICTIONARY LOOKUP

def dictionary_lookup(transaction_id):
    """
    Dictionary Lookup — O(1)
    Jumps directly to the record using ID as a key.
    """
    return transactions_dict.get(transaction_id, None)

# REQUEST HANDLER

class MoMoAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.address_string()}] {format % args}")

    # GET

    def do_GET(self):
        # Check authentication first
        if not check_auth(self):
            send_unauthorized(self)
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = path.split("/")

        # GET /transactions return all transactions first 50 for performance
        if path == "/transactions":

            from urllib.parse import parse_qs
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", [50])[0])
            type_filter = params.get("type", [None])[0]

            results = transactions_list
            if type_filter:
                results = [t for t in results if t["type"].lower() == type_filter.lower()]

            send_json(self, 200, {
                "total": len(results),
                "showing": min(limit, len(results)),
                "transactions": results[:limit]
            })

        # GET /transactions/{id} return one transaction By ID
        elif len(parts) == 3 and parts[1] == "transactions" and parts[2].isdigit():
            transaction_id = int(parts[2])

            # Use dictionary lookup O(1) for efficiency
            transaction = dictionary_lookup(transaction_id)

            if transaction:
                send_json(self, 200, transaction)
            else:
                send_json(self, 404, {
                    "error": "Not Found",
                    "message": f"Transaction with ID {transaction_id} does not exist."
                })

        # GET /health
        elif path == "/health":
            send_json(self, 200, {
                "status": "ok",
                "total_transactions": len(transactions_list),
                "api": "MoMo Data Pipeline API",
                "team": "Team Nexus"
            })

        else:
            send_json(self, 404, {
                "error": "Not Found",
                "message": f"Endpoint {path} does not exist."
            })

    # POST

    def do_POST(self):
        if not check_auth(self):
            send_unauthorized(self)
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # POST /transactions add a new transaction
        if path == "/transactions":
            content_length = int(self.headers.get("Content-Length", 0))

            if content_length == 0:
                send_json(self, 400, {
                    "error": "Bad Request",
                    "message": "Request body is empty. Please send a JSON object."
                })
                return

            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {
                    "error": "Bad Request",
                    "message": "Invalid JSON format in request body."
                })
                return

            # Validate required fields
            required = ["type", "amount"]
            missing = [f for f in required if f not in data]
            if missing:
                send_json(self, 400, {
                    "error": "Bad Request",
                    "message": f"Missing required fields: {', '.join(missing)}"
                })
                return

            # Validate amount
            if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
                send_json(self, 400, {
                    "error": "Bad Request",
                    "message": "Amount must be a positive number."
                })
                return

            # Create new transaction
            new_id = max(transactions_dict.keys()) + 1 if transactions_dict else 1
            new_transaction = {
                "id": new_id,
                "transaction_id": data.get("transaction_id"),
                "type": data.get("type", "Other"),
                "amount": float(data["amount"]),
                "fee": float(data.get("fee", 0)),
                "sender": data.get("sender"),
                "receiver": data.get("receiver"),
                "new_balance": data.get("new_balance"),
                "date": data.get("date", ""),
                "timestamp_ms": data.get("timestamp_ms", 0),
                "raw_body": data.get("raw_body", "")
            }

            # Add to both list and dictionary
            transactions_list.append(new_transaction)
            transactions_dict[new_id] = new_transaction

            send_json(self, 201, {
                "message": "Transaction created successfully.",
                "transaction": new_transaction
            })

        else:
            send_json(self, 404, {
                "error": "Not Found",
                "message": f"Endpoint {path} does not exist."
            })

    # PUT

    def do_PUT(self):
        if not check_auth(self):
            send_unauthorized(self)
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = path.split("/")

        # PUT /transactions/{id} update an existing transaction
        if len(parts) == 3 and parts[1] == "transactions" and parts[2].isdigit():
            transaction_id = int(parts[2])
            transaction = dictionary_lookup(transaction_id)

            if not transaction:
                send_json(self, 404, {
                    "error": "Not Found",
                    "message": f"Transaction with ID {transaction_id} does not exist."
                })
                return

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                updates = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {
                    "error": "Bad Request",
                    "message": "Invalid JSON format in request body."
                })
                return

            # Validate amount if provided
            if "amount" in updates:
                if not isinstance(updates["amount"], (int, float)) or updates["amount"] <= 0:
                    send_json(self, 400, {
                        "error": "Bad Request",
                        "message": "Amount must be a positive number."
                    })
                    return

            # Update fields (cannot update id)
            protected = ["id"]
            for key, value in updates.items():
                if key not in protected:
                    transaction[key] = value

            # Update dictionary too
            transactions_dict[transaction_id] = transaction

            send_json(self, 200, {
                "message": "Transaction updated successfully.",
                "transaction": transaction
            })

        else:
            send_json(self, 404, {
                "error": "Not Found",
                "message": f"Endpoint {path} does not exist."
            })

    # DELETE

    def do_DELETE(self):
        if not check_auth(self):
            send_unauthorized(self)
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = path.split("/")

        # DELETE /transactions/{id} delete a transaction BY ID
        if len(parts) == 3 and parts[1] == "transactions" and parts[2].isdigit():
            transaction_id = int(parts[2])
            transaction = dictionary_lookup(transaction_id)

            if not transaction:
                send_json(self, 404, {
                    "error": "Not Found",
                    "message": f"Transaction with ID {transaction_id} does not exist."
                })
                return

            # Remove from both list and dictionary
            transactions_list.remove(transaction)
            del transactions_dict[transaction_id]

            send_json(self, 200, {
                "message": f"Transaction {transaction_id} deleted successfully."
            })

        else:
            send_json(self, 404, {
                "error": "Not Found",
                "message": f"Endpoint {path} does not exist."
            })

# START SERVER


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), MoMoAPIHandler)
    print(f"\n{'='*50}")
    print(f"  MoMo Data Pipeline API — Team Nexus")
    print(f"  Running at http://{HOST}:{PORT}")
    print(f"{'='*50}\n")
    print("Available endpoints:")
    print("  GET    /transactions")
    print("  GET    /transactions/{id}")
    print("  POST   /transactions")
    print("  PUT    /transactions/{id}")
    print("  DELETE /transactions/{id}")
    print("  GET    /health")
    print(f"\nPress Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")