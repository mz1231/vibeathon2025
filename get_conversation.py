#!/usr/bin/env python3
"""
Interactive chat viewer - pick a conversation and see all messages.
Usage: python get_conversation.py
"""

from imessage_extractor import iMessageExtractor


def main():
    extractor = iMessageExtractor()

    # Get all chats
    chats = extractor.get_all_chats()

    print("=" * 60)
    print("Available Chats")
    print("=" * 60)
    print()

    # Display all chats with numbers for selection
    for i, chat in enumerate(chats):
        name = chat["display_name"] or chat["chat_identifier"]
        chat_type = "Group" if chat["is_group"] else "Direct"
        participants = len(chat["participants"])
        print(f"  {i + 1}. [{chat['chat_id']}] {name} ({chat_type}, {participants} participant(s))")

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

            idx = int(selection) - 1
            if 0 <= idx < len(chats):
                selected_chat = chats[idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(chats)}")
        except ValueError:
            print("Please enter a valid number")

    # Get messages for selected chat
    chat_id = selected_chat["chat_id"]
    chat_name = selected_chat["display_name"] or selected_chat["chat_identifier"]

    print()
    print("=" * 60)
    print(f"Conversation: {chat_name}")
    print(f"Chat ID: {chat_id}")
    print(f"Participants: {', '.join(selected_chat['participants'])}")
    print("=" * 60)
    print()

    # Get ALL messages for this chat (no direct_only filter)
    messages = extractor.get_messages(chat_id=chat_id)

    if not messages:
        print("No messages found in this chat.")
    else:
        print(f"Total messages: {len(messages)}")
        print()

        for msg in messages:
            sender = "Me" if msg['is_from_me'] else msg['sender']
            timestamp = msg['timestamp'][:16] if msg['timestamp'] else "Unknown"

            # Handle different message types
            if msg['text']:
                text = msg['text']
            elif msg['has_attachments']:
                text = "[Attachment]"
            else:
                text = "[Reaction/Tapback]"

            print(f"[{timestamp}] {sender}:")
            print(f"  {text}")
            print()

    # Option to export
    export = input("Export to JSON? (y/n): ").strip().lower()
    if export == 'y':
        filename = f"chat_{chat_id}_export.json"
        extractor.export_to_json({
            "chat_id": chat_id,
            "chat_name": chat_name,
            "participants": selected_chat["participants"],
            "message_count": len(messages),
            "messages": messages
        }, filename)
        print(f"Exported to {filename}")

    extractor.close()


if __name__ == "__main__":
    main()
