import xml.etree.ElementTree as ET
import json

# Load XML file
tree = ET.parse("data/modified_sms_v2.xml")
root = tree.getroot()

records = []

# Loop through every SMS
for sms in root.findall("sms"):
    record = {
        "address": sms.get("address"),
        "date": sms.get("date"),
        "readable_date": sms.get("readable_date"),
        "body": sms.get("body"),
        "type": sms.get("type")
    }

    records.append(record)

print(f"Total records found: {len(records)}")

# Save JSON output
with open("examples/sms_records.json", "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4)

print("JSON file created successfully.")