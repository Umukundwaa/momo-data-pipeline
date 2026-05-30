import json
import re

# Load SMS records
with open("examples/sms_records.json", "r", encoding="utf-8") as file:
    records = json.load(file)

transactions = []

for sms in records:

    body = sms.get("body", "")

    transaction = {
        "transaction_type": "unknown",
        "amount": None,
        "sender": None,
        "receiver": None,
        "transaction_id": None,
        "date": sms.get("readable_date")
    }

    # --------------------
    # Incoming Money
    # --------------------
    if "You have received" in body:

        transaction["transaction_type"] = "incoming_money"

        amount_match = re.search(
            r"You have received ([\d,]+) RWF",
            body
        )

        sender_match = re.search(
            r"from (.*?) \(",
            body
        )

        txid_match = re.search(
            r"Financial Transaction Id: (\d+)",
            body
        )

        if amount_match:
            transaction["amount"] = amount_match.group(1)

        if sender_match:
            transaction["sender"] = sender_match.group(1)

        if txid_match:
            transaction["transaction_id"] = txid_match.group(1)

    # --------------------
    # Payment
    # --------------------
    elif "Your payment of" in body:

        transaction["transaction_type"] = "payment"

        amount_match = re.search(
            r"Your payment of ([\d,]+) RWF",
            body
        )

        receiver_match = re.search(
            r"to (.*?) \d+ has been completed",
            body
        )

        txid_match = re.search(
            r"TxId:\s*(\d+)",
            body
        )

        if amount_match:
            transaction["amount"] = amount_match.group(1)

        if receiver_match:
            transaction["receiver"] = receiver_match.group(1)

        if txid_match:
            transaction["transaction_id"] = txid_match.group(1)

    # --------------------
    # Bank Deposit
    # --------------------
    elif "bank deposit" in body.lower():

        transaction["transaction_type"] = "bank_deposit"

        amount_match = re.search(
            r"bank deposit of ([\d,]+) RWF",
            body,
            re.IGNORECASE
        )

        if amount_match:
            transaction["amount"] = amount_match.group(1)

    if transaction["transaction_type"] != "unknown":
        transactions.append(transaction)

print(f"Transactions extracted: {len(transactions)}")

with open(
    "examples/transactions.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        transactions,
        file,
        indent=4
    )

print("transactions.json created successfully")