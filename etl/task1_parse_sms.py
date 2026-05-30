import xml.etree.ElementTree as ET
import re
import json


def categorize(body):
    if "You have received" in body:
        return "Incoming Money"
    elif "bank deposit" in body.lower():
        return "Bank Deposit"
    elif "transferred to" in body:
        return "Transfer to Mobile"
    elif "Airtime" in body or "airtime" in body:
        return "Airtime Bill"
    elif "Your payment of" in body:
        return "Payment to Code"
    else:
        return "Other"


def extract_amount(body):
    match = re.search(r'(\d[\d,]*)\s*RWF', body)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0.0


def extract_fee(body):
    match = re.search(r'[Ff]ee was[:\s]*(\d+)\s*RWF', body)
    if match:
        return float(match.group(1))
    return 0.0


def extract_transaction_id(body):
    match = re.search(r'(?:TxId:|Financial Transaction Id:)\s*(\d+)', body)
    if match:
        return match.group(1)
    return None


def extract_sender(body):
    match = re.search(r'received \d[\d,]* RWF from ([^(]+)', body)
    if match:
        return match.group(1).strip()
    match = re.search(r'transferred to ([^(]+)\(', body)
    if match:
        return match.group(1).strip()
    return None


def extract_receiver(body):
    match = re.search(r'payment of \d[\d,]* RWF to ([A-Za-z ]+\d+)', body)
    if match:
        return match.group(1).strip()
    return None


def extract_balance(body):
    match = re.search(r'[Nn]ew balance[:\s](\d[\d,])\s*RWF', body)
    if match:
        return float(match.group(1).replace(',', ''))
    match = re.search(r'NEW BALANCE\s*:(\d[\d,]*)\s*RWF', body)
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def parse_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    transactions = []

    for index, sms in enumerate(root.findall('sms'), start=1):
        body = sms.get('body', '')
        date_ms = sms.get('date', '0')
        readable_date = sms.get('readable_date', '')

        transaction = {
            "id": index,
            "transaction_id": extract_transaction_id(body),
            "type": categorize(body),
            "amount": extract_amount(body),
            "fee": extract_fee(body),
            "sender": extract_sender(body),
            "receiver": extract_receiver(body),
            "new_balance": extract_balance(body),
            "date": readable_date,
            "timestamp_ms": int(date_ms),
            "raw_body": body
        }

        transactions.append(transaction)

    return transactions


if __name__ == "__main__":
    transactions = parse_xml("data/modified_sms_v2.xml")
    print(f"Total transactions parsed: {len(transactions)}")
    print(json.dumps(transactions[:3], indent=2))

    with open("data/parsed_sms.json", "w") as f:
        json.dump(transactions, f, indent=2)