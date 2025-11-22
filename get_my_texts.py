#!/usr/bin/env python3
"""
Get all text messages sent by me (excluding reactions).
Usage: python get_my_texts.py
"""

from imessage_extractor import iMessageExtractor


def main():
    extractor = iMessageExtractor()

    # Get all chats
    chats = extractor.get_all_chats()

    print("=" * 60)
    print("Select a Chat (or 0 for all chats)")
    print("=" * 60)
    print()
    print("  0. [ALL] Get my texts from all conversations")
    print()

    # Display all chats with numbers for selection
    for i, chat in enumerate(chats):
        name = chat["display_name"] or chat["chat_identifier"]
        chat_type = "Group" if chat["is_group"] else "Direct"
        print(f"  {i + 1}. [{chat['chat_id']}] {name} ({chat_type})")

    print()
    print("=" * 60)

    # Get user selection
    while True:
        try:
            selection = input("Enter chat number (or 'q' to quit): ").strip()
            if selection.lower() == 'q':
                print("Goodbye!")
                extractor.close()
                return

            idx = int(selection)
            if idx == 0:
                # All chats
                selected_chat = None
                chat_id = None
                chat_name = "All Conversations"
                break
            elif 1 <= idx <= len(chats):
                selected_chat = chats[idx - 1]
                chat_id = selected_chat["chat_id"]
                chat_name = selected_chat["display_name"] or selected_chat["chat_identifier"]
                break
            else:
                print(f"Please enter a number between 0 and {len(chats)}")
        except ValueError:
            print("Please enter a valid number")

    print()
    print("=" * 60)
    print(f"My Texts in: {chat_name}")
    print("=" * 60)
    print()

    # Get my texts for selected chat (or all)
    my_texts = extractor.get_my_texts(chat_id=chat_id)

    print(f"Total texts sent: {len(my_texts)}")
    print()

    if not my_texts:
        print("No texts found.")
    else:
        for msg in my_texts:
            timestamp = msg['timestamp'][:16] if msg['timestamp'] else "Unknown"
            recipient = msg['chat_name'] or msg['recipient'] or msg['chat_identifier']
            text = msg['text']

            print(f"[{timestamp}] To: {recipient}")
            print(f"  {text}")
            print()

    # Option to export
    export = input("Export to JSON? (y/n): ").strip().lower()
    if export == 'y':
        if chat_id:
            filename = f"my_texts_chat_{chat_id}.json"
        else:
            filename = "my_texts_all.json"

        extractor.export_to_json({
            "chat_id": chat_id,
            "chat_name": chat_name,
            "total_count": len(my_texts),
            "messages": my_texts
        }, filename)
        print(f"Exported to {filename}")

    extractor.close()


if __name__ == "__main__":
    main()
