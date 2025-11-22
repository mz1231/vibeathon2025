#!/usr/bin/env python3
"""
Export text messages sent by me to JSON.
Usage:
    python export_my_texts.py                    # All my texts
    python export_my_texts.py 100                # Last 100 texts
    python export_my_texts.py 100 +17325671523   # Last 100 texts to specific number
"""

import sys
from imessage_extractor import iMessageExtractor


def main():
    extractor = iMessageExtractor()

    # Parse arguments
    limit = None
    contact = None

    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
        else:
            contact = arg

    # Get my texts (optionally filtered by contact)
    my_texts = extractor.get_my_texts(contact_identifier=contact)

    # Get most recent N texts if limit specified
    if limit:
        my_texts = my_texts[-limit:]

    if contact:
        print(f"My texts to {contact}: {len(my_texts)}")
        filename = f"my_texts_to_{contact.replace('+', '')}.json"
    else:
        print(f"Total texts: {len(my_texts)}")
        filename = "my_texts.json"

    # Export just the text content
    texts_only = [msg["text"] for msg in my_texts]

    extractor.export_to_json(texts_only, filename)

    extractor.close()


if __name__ == "__main__":
    main()
