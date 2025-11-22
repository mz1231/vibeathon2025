#!/usr/bin/env python3
"""
Export text messages sent by me to JSON.
Usage:
    python export_my_texts.py                    # All my texts
    python export_my_texts.py +17325671523       # My texts to specific number
"""

import sys
from imessage_extractor import iMessageExtractor


def main():
    extractor = iMessageExtractor()

    # Check if phone number provided
    contact = sys.argv[1] if len(sys.argv) > 1 else None

    # Get my texts (optionally filtered by contact)
    my_texts = extractor.get_my_texts(contact_identifier=contact)

    if contact:
        print(f"My texts to {contact}: {len(my_texts)}")
        filename = f"my_texts_to_{contact.replace('+', '')}.json"
    else:
        print(f"Total texts sent: {len(my_texts)}")
        filename = "my_texts.json"

    # Export to JSON
    extractor.export_to_json({
        "contact": contact,
        "total_count": len(my_texts),
        "messages": my_texts
    }, filename)

    extractor.close()


if __name__ == "__main__":
    main()
