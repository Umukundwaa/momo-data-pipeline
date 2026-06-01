"""Simple XML parser for MoMo SMS transactions.

Provides a `parse_xml` function that returns a list of transaction dicts.
The function is intentionally tolerant: it will extract common fields if
present and return an empty list when the file can't be read.
"""
from typing import List, Dict
import xml.etree.ElementTree as ET
import os


def parse_xml(file_path: str) -> List[Dict]:
    """Parse the given XML file and return a list of transaction dicts.

    The parser attempts to find transaction elements under the root and
    extract common child tags or attributes such as `id`, `sender`,
    `receiver`, `amount` and `date`. Unknown fields are included as raw
    text values.
    """
    if not os.path.exists(file_path):
        return []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError:
        return []

    transactions: List[Dict] = []

    # heuristic: find all elements named 'transaction' (case-insensitive)
    for tx in root.findall('.//sms'):
        tx_dict: Dict = {}

        # try attributes first
        for k, v in tx.attrib.items():
            tx_dict[k] = v

        # then child elements
        for child in list(tx):
            tag = child.tag.lower()
            text = child.text.strip() if child.text else ''
            tx_dict[tag] = text

        # ensure there's an 'id' key
        if 'id' not in tx_dict:
            # try common alternatives
            if 'transaction_id' in tx_dict:
                tx_dict['id'] = tx_dict.pop('transaction_id')
            else:
                # fallback: generate an id from position
                tx_dict['id'] = len(transactions) + 1

        transactions.append(tx_dict)

    return transactions
