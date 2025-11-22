#!/usr/bin/env python3
"""
iMessage Extractor
Extracts messages from the macOS iMessage database and exports to JSON.
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from typing import Optional


class iMessageExtractor:
    # Apple's timestamp epoch (2001-01-01) offset from Unix epoch
    APPLE_EPOCH_OFFSET = 978307200

    def __init__(self, db_path: str = "./databases/chat.db"):
        """
        Initialize the extractor.

        Args:
            db_path: Path to chat.db file. Defaults to ./chat.db
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database not found at {db_path}. "
                "Please place your chat.db file in the project directory."
            )

        self.db_path = db_path
        # Open in read-only mode to prevent creating WAL files
        self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to database: {self.db_path}")

    def _convert_apple_timestamp(self, timestamp: int) -> str:
        """Convert Apple's timestamp to ISO format string."""
        if timestamp is None:
            return None

        # Handle both nanosecond and second formats
        if timestamp > 1e12:
            timestamp = timestamp / 1e9

        unix_timestamp = timestamp + self.APPLE_EPOCH_OFFSET
        return datetime.fromtimestamp(unix_timestamp).isoformat()

    def _extract_text_from_attributed_body(self, attributed_body: bytes) -> str:
        """Extract plain text from attributedBody blob (used in newer macOS)."""
        if not attributed_body:
            return None

        try:
            # The text is embedded in the binary blob
            # Look for the NSString content between specific markers
            text = attributed_body.decode('utf-8', errors='ignore')

            # Try to find text between common patterns
            # Pattern 1: After "NSString" marker
            if 'NSString' in text:
                # Extract readable text, filtering out control characters
                readable = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
                # Clean up and get the main content
                lines = [l.strip() for l in readable.split('\n') if l.strip() and len(l.strip()) > 1]
                if lines:
                    # Usually the actual message is one of the longer strings
                    return max(lines, key=len) if lines else None

            # Pattern 2: Try to extract directly
            # Remove null bytes and control characters
            cleaned = re.sub(rb'[\x00-\x1f\x7f-\x9f]', b' ', attributed_body)
            decoded = cleaned.decode('utf-8', errors='ignore').strip()

            # Find the longest sequence of printable characters
            matches = re.findall(r'[\x20-\x7E]{2,}', decoded)
            if matches:
                # Filter out metadata-like strings
                content = [m for m in matches if not any(x in m.lower() for x in ['nsstring', 'nsattributed', 'nsmutable', '__kIMMessagePartAttributeName'])]
                if content:
                    return max(content, key=len)

            return None
        except Exception:
            return None

    def get_all_contacts(self) -> list[dict]:
        """Get all contacts/handles from the database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                h.ROWID as handle_id,
                h.id as identifier,
                h.service
            FROM handle h
            ORDER BY h.id
        """)

        contacts = []
        for row in cursor.fetchall():
            contacts.append({
                "handle_id": row["handle_id"],
                "identifier": row["identifier"],
                "service": row["service"]
            })

        return contacts

    def get_all_chats(self) -> list[dict]:
        """Get all chat threads with participant info."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                c.ROWID as chat_id,
                c.chat_identifier,
                c.display_name,
                c.service_name,
                GROUP_CONCAT(h.id) as participants
            FROM chat c
            LEFT JOIN chat_handle_join chj ON c.ROWID = chj.chat_id
            LEFT JOIN handle h ON chj.handle_id = h.ROWID
            GROUP BY c.ROWID
            ORDER BY c.ROWID
        """)

        chats = []
        for row in cursor.fetchall():
            participants = row["participants"].split(",") if row["participants"] else []
            chats.append({
                "chat_id": row["chat_id"],
                "chat_identifier": row["chat_identifier"],
                "display_name": row["display_name"],
                "service": row["service_name"],
                "participants": participants,
                "is_group": len(participants) > 1
            })

        return chats

    def get_messages(
        self,
        chat_id: Optional[int] = None,
        contact_identifier: Optional[str] = None,
        limit: Optional[int] = None,
        only_from_me: bool = False,
        only_to_me: bool = False,
        direct_only: bool = False
    ) -> list[dict]:
        """
        Extract messages with optional filtering.

        Args:
            chat_id: Filter by specific chat/thread ID
            contact_identifier: Filter by contact (phone/email)
            limit: Maximum number of messages to return
            only_from_me: Only include messages I sent
            only_to_me: Only include messages sent to me
            direct_only: Only include 1-on-1 conversations (no group chats)

        Returns:
            List of message dictionaries
        """
        cursor = self.conn.cursor()

        query = """
            SELECT
                m.ROWID as message_id,
                m.text,
                m.is_from_me,
                m.date,
                m.date_read,
                m.date_delivered,
                m.service,
                m.cache_has_attachments,
                h.id as sender_identifier,
                c.ROWID as chat_id,
                c.chat_identifier,
                c.display_name as chat_name
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            LEFT JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
            LEFT JOIN chat c ON cmj.chat_id = c.ROWID
            WHERE 1=1
        """

        params = []

        if chat_id is not None:
            query += " AND c.ROWID = ?"
            params.append(chat_id)

        if contact_identifier is not None:
            query += " AND (h.id LIKE ? OR c.chat_identifier LIKE ?)"
            params.extend([f"%{contact_identifier}%", f"%{contact_identifier}%"])

        if direct_only:
            # Filter for 1-on-1 chats only (chats with exactly 1 participant)
            query += """ AND c.ROWID IN (
                SELECT chat_id FROM chat_handle_join
                GROUP BY chat_id
                HAVING COUNT(*) = 1
            )"""

        if only_from_me:
            query += " AND m.is_from_me = 1"
        elif only_to_me:
            query += " AND m.is_from_me = 0"

        query += " ORDER BY m.date ASC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "message_id": row["message_id"],
                "text": row["text"],
                "is_from_me": bool(row["is_from_me"]),
                "timestamp": self._convert_apple_timestamp(row["date"]),
                "date_read": self._convert_apple_timestamp(row["date_read"]),
                "date_delivered": self._convert_apple_timestamp(row["date_delivered"]),
                "service": row["service"],
                "has_attachments": bool(row["cache_has_attachments"]),
                "sender": "me" if row["is_from_me"] else row["sender_identifier"],
                "chat_id": row["chat_id"],
                "chat_identifier": row["chat_identifier"],
                "chat_name": row["chat_name"]
            })

        return messages

    def get_conversation(self, contact_identifier: str, direct_only: bool = True) -> dict:
        """
        Get a full conversation with a specific contact.

        Args:
            contact_identifier: Phone number or email to filter by
            direct_only: Only include 1-on-1 conversations (default True)

        Returns:
            Dictionary with conversation metadata and messages
        """
        messages = self.get_messages(contact_identifier=contact_identifier, direct_only=direct_only)

        if not messages:
            return {
                "contact": contact_identifier,
                "message_count": 0,
                "messages": []
            }

        return {
            "contact": contact_identifier,
            "chat_id": messages[0]["chat_id"] if messages else None,
            "chat_name": messages[0]["chat_name"] if messages else None,
            "message_count": len(messages),
            "first_message": messages[0]["timestamp"] if messages else None,
            "last_message": messages[-1]["timestamp"] if messages else None,
            "messages": messages
        }

    def get_my_texts(
        self,
        chat_id: Optional[int] = None,
        contact_identifier: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[dict]:
        """
        Get all text messages sent by me (excluding reactions/tapbacks).

        Args:
            chat_id: Filter by specific chat/thread ID
            contact_identifier: Filter by contact (phone/email)
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries containing only my sent texts
        """
        cursor = self.conn.cursor()

        query = """
            SELECT
                m.ROWID as message_id,
                m.text,
                m.attributedBody,
                m.is_from_me,
                m.date,
                m.date_delivered,
                m.service,
                m.cache_has_attachments,
                h.id as recipient_identifier,
                c.ROWID as chat_id,
                c.chat_identifier,
                c.display_name as chat_name
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            LEFT JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
            LEFT JOIN chat c ON cmj.chat_id = c.ROWID
            WHERE m.is_from_me = 1
              AND (m.text IS NOT NULL OR m.attributedBody IS NOT NULL)
              AND m.associated_message_type = 0
        """

        params = []

        if chat_id is not None:
            query += " AND c.ROWID = ?"
            params.append(chat_id)

        if contact_identifier is not None:
            query += " AND (h.id LIKE ? OR c.chat_identifier LIKE ?)"
            params.extend([f"%{contact_identifier}%", f"%{contact_identifier}%"])

        query += " ORDER BY m.date ASC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)

        messages = []
        for row in cursor.fetchall():
            # Try text first, fall back to attributedBody
            text = row["text"]
            if not text and row["attributedBody"]:
                text = self._extract_text_from_attributed_body(row["attributedBody"])

            # Skip if no text could be extracted
            if not text:
                continue

            messages.append({
                "message_id": row["message_id"],
                "text": text,
                "timestamp": self._convert_apple_timestamp(row["date"]),
                "date_delivered": self._convert_apple_timestamp(row["date_delivered"]),
                "service": row["service"],
                "has_attachments": bool(row["cache_has_attachments"]),
                "recipient": row["recipient_identifier"],
                "chat_id": row["chat_id"],
                "chat_identifier": row["chat_identifier"],
                "chat_name": row["chat_name"]
            })

        return messages

    def export_to_json(self, data: dict | list, output_path: str):
        """Export data to a JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Exported to {output_path}")

    def get_stats(self) -> dict:
        """Get statistics about the message database."""
        cursor = self.conn.cursor()

        # Total messages
        cursor.execute("SELECT COUNT(*) FROM message")
        total_messages = cursor.fetchone()[0]

        # Messages from me
        cursor.execute("SELECT COUNT(*) FROM message WHERE is_from_me = 1")
        from_me = cursor.fetchone()[0]

        # Total chats
        cursor.execute("SELECT COUNT(*) FROM chat")
        total_chats = cursor.fetchone()[0]

        # Total contacts
        cursor.execute("SELECT COUNT(*) FROM handle")
        total_contacts = cursor.fetchone()[0]

        return {
            "total_messages": total_messages,
            "messages_from_me": from_me,
            "messages_to_me": total_messages - from_me,
            "total_chats": total_chats,
            "total_contacts": total_contacts
        }

    def close(self):
        """Close the database connection."""
        self.conn.close()


def main():
    """Example usage of the iMessage extractor."""

    print("=" * 50)
    print("iMessage Extractor")
    print("=" * 50)

    try:
        # Initialize extractor (copies database automatically)
        extractor = iMessageExtractor()

        # Get database stats
        print("\n📊 Database Statistics:")
        stats = extractor.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # List all chats
        print("\n💬 Available Chats:")
        chats = extractor.get_all_chats()
        for i, chat in enumerate(chats[:10]):  # Show first 10
            name = chat["display_name"] or chat["chat_identifier"]
            chat_type = "Group" if chat["is_group"] else "Direct"
            print(f"  [{chat['chat_id']}] {name} ({chat_type})")

        if len(chats) > 10:
            print(f"  ... and {len(chats) - 10} more")

        # Export all data
        print("\n📁 Exporting data...")

        # Export all messages
        all_messages = extractor.get_messages()
        extractor.export_to_json({
            "stats": stats,
            "messages": all_messages
        }, "all_messages.json")

        # Export chat list
        extractor.export_to_json(chats, "chats.json")

        print("\n✅ Export complete!")
        print("\nUsage examples:")
        print("  # Get conversation with specific contact:")
        print('  conv = extractor.get_conversation("+1234567890")')
        print("  # Get only messages I sent:")
        print("  my_msgs = extractor.get_messages(only_from_me=True)")
        print("  # Get messages from specific chat:")
        print("  chat_msgs = extractor.get_messages(chat_id=5)")

        extractor.close()

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo fix this:")
        print("1. Open System Preferences → Privacy & Security → Full Disk Access")
        print("2. Add Terminal.app or your IDE")
        print("3. Restart your terminal and try again")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
