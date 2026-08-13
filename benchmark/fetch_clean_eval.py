"""Fetch upstream usaddress's held-out labeled test data (the pre-registered
clean eval set, see eval/PROTOCOL.md) and convert the parserator XML into
eval/clean/clean.jsonl: {raw, tokens, labels}.

The XML wraps each token in its label element:
  <AddressString><AddressNumber>123</AddressNumber> <StreetName>Main</StreetName>...</AddressString>
Raw text is reconstructed by space-joining tokens (tokens never contain spaces).
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# us50_test_tagged.xml is deliberately excluded: it labels whole street phrases
# as StreetName (coarser than the model's schema — e.g. "Road," tagged StreetName),
# so it measures convention mismatch, not accuracy. See eval/PROTOCOL.md changelog.
FILES = ["labeled.xml", "multi_word_state_addresses.xml", "simple_address_patterns.xml"]
BASE = "https://raw.githubusercontent.com/datamade/usaddress/main/measure_performance/test_data/"
OUT = Path(__file__).parent.parent / "eval" / "clean" / "clean.jsonl"


def parse_xml(text, source):
    root = ET.fromstring(text)
    rows = []
    for addr in root.iter("AddressString"):
        tokens, labels = [], []
        for el in addr:
            token = (el.text or "").strip()
            if token:
                tokens.append(token)
                labels.append(el.tag)
        if tokens:
            rows.append({"raw": " ".join(tokens), "tokens": tokens, "labels": labels, "source": source})
    return rows


def main():
    rows = []
    for name in FILES:
        with urllib.request.urlopen(BASE + name, timeout=60) as resp:
            rows += parse_xml(resp.read().decode("utf-8"), name)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} labeled clean-eval rows -> {OUT}")


if __name__ == "__main__":
    main()
