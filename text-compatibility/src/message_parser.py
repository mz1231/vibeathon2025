"""
Message Parser Module
=====================
Handles parsing iMessage data from:
1. macOS SQLite database (chat.db)
2. JSON file uploads (for manual exports)

This module extracts messages and prepares them for embedding.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """Represents a single message."""
    id: str
    text: str
    timestamp: str
    sender_id: str
    is_from_me: bool
    conversation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MessageWindow:
    """
    A message with its surrounding context.
    
    We embed message WINDOWS, not individual messages, because:
    - "sure" alone is meaningless
    - "Q: want to hang out? A: sure" shows agreement to plans
    
    The window captures conversational context.
    """
    message_id: str
    message_text: str
    context: str  # The surrounding messages formatted as conversation
    sender_id: str
    timestamp: str
    is_from_me: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IMessageParser:
    """
    Parser for macOS iMessage SQLite database.
    
    The database is located at: ~/Library/Messages/chat.db
    
    IMPORTANT: Requires Full Disk Access permission on macOS.
    System Preferences > Security & Privacy > Privacy > Full Disk Access
    """
    
    # macOS timestamps start from 2001-01-01 (Apple's epoch)
    # and are stored in nanoseconds
    MAC_EPOCH = datetime(2001, 1, 1)
    
    def __init__(self, db_path: str = None):
        """
        Initialize the parser.
        
        Args:
            db_path: Path to chat.db. Defaults to ~/Library/Messages/chat.db
        """
        if db_path is None:
            db_path = Path.home() / "Library" / "Messages" / "chat.db"
        self.db_path = Path(db_path)
        
    def _convert_timestamp(self, mac_timestamp: int) -> str:
        """
        Convert macOS timestamp to ISO format string.
        
        macOS stores timestamps as nanoseconds since 2001-01-01.
        """
        if mac_timestamp is None:
            return datetime.now().isoformat()
        
        # Convert nanoseconds to seconds
        seconds = mac_timestamp / 1_000_000_000
        actual_time = self.MAC_EPOCH + timedelta(seconds=seconds)
        return actual_time.isoformat()
    
    def list_conversations(self) -> List[Dict]:
        """
        List all available conversations in the database.
        
        Returns:
            List of dicts with conversation_id and display_name
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
        SELECT 
            chat.chat_identifier,
            chat.display_name,
            COUNT(chat_message_join.message_id) as message_count
        FROM chat
        LEFT JOIN chat_message_join ON chat.ROWID = chat_message_join.chat_id
        GROUP BY chat.ROWID
        ORDER BY message_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'conversation_id': row[0],
                'display_name': row[1] or row[0],  # Fall back to identifier if no name
                'message_count': row[2]
            })
        
        return conversations
    
    def parse_conversation(self, chat_identifier: str) -> List[Message]:
        """
        Extract all messages from a specific conversation.
        
        Args:
            chat_identifier: Phone number, email, or group chat ID
            
        Returns:
            List of Message objects, sorted by timestamp
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
        SELECT 
            message.ROWID,
            message.text,
            message.date,
            message.is_from_me,
            handle.id as sender_identifier,
            chat.chat_identifier
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.ROWID
        LEFT JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
        LEFT JOIN chat ON chat_message_join.chat_id = chat.ROWID
        WHERE chat.chat_identifier = ?
        ORDER BY message.date ASC
        """
        
        cursor.execute(query, (chat_identifier,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg_id, text, timestamp, is_from_me, sender, conv_id = row
            
            # Skip empty messages (reactions, attachments without text)
            if not text or text.strip() == '':
                continue
            
            # Clean the text
            text = self._clean_text(text)
            
            messages.append(Message(
                id=str(msg_id),
                text=text,
                timestamp=self._convert_timestamp(timestamp),
                sender_id='me' if is_from_me else (sender or 'unknown'),
                is_from_me=bool(is_from_me),
                conversation_id=conv_id
            ))
        
        return messages
    
    def _clean_text(self, text: str) -> str:
        """Clean message text by removing special characters."""
        if text is None:
            return ''
        
        # Remove the special object replacement character (used for attachments)
        text = text.replace('\ufffc', '')
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text.strip()


class JSONParser:
    """
    Parser for JSON message exports.
    
    Expected format:
    {
        "conversation_id": "uuid",
        "participants": ["user_1", "user_2"],
        "messages": [
            {
                "id": "msg_uuid",
                "sender_id": "user_1",
                "text": "Message content",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        ]
    }
    """
    
    def __init__(self, my_user_id: str):
        """
        Initialize the parser.
        
        Args:
            my_user_id: The user ID that represents "me" in the conversation
        """
        self.my_user_id = my_user_id
    
    def parse_file(self, file_path: str) -> List[Message]:
        """
        Parse messages from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of Message objects
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.parse_data(data)
    
    def parse_data(self, data: Dict) -> List[Message]:
        """
        Parse messages from a dictionary.
        
        Args:
            data: Dictionary containing conversation data
            
        Returns:
            List of Message objects
        """
        messages = []
        conversation_id = data.get('conversation_id', 'unknown')
        
        for msg in data.get('messages', []):
            # Skip empty messages
            text = msg.get('text', '')
            if not text or text.strip() == '':
                continue
            
            sender_id = msg.get('sender_id', 'unknown')
            is_from_me = sender_id == self.my_user_id
            
            messages.append(Message(
                id=str(msg.get('id', '')),
                text=text.strip(),
                timestamp=msg.get('timestamp', ''),
                sender_id=sender_id,
                is_from_me=is_from_me,
                conversation_id=conversation_id
            ))
        
        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        
        return messages


def create_message_windows(
    messages: List[Message],
    window_size: int = 3
) -> List[MessageWindow]:
    """
    Create context windows around each message.
    
    Why windows instead of individual messages?
    ------------------------------------------
    The message "lol ok" by itself tells us almost nothing.
    But in context:
        A: "I just tripped and spilled coffee everywhere"
        B: "lol ok"
    We learn that B responds to mishaps with casual amusement.
    
    The window captures this conversational flow.
    
    Args:
        messages: List of Message objects
        window_size: Number of messages before AND after to include
        
    Returns:
        List of MessageWindow objects
    """
    windows = []
    
    for i, msg in enumerate(messages):
        # Get surrounding messages for context
        start_idx = max(0, i - window_size)
        end_idx = min(len(messages), i + window_size + 1)
        
        # Build the context string
        context_parts = []
        for j in range(start_idx, end_idx):
            sender_label = "Me" if messages[j].is_from_me else "Them"
            context_parts.append(f"{sender_label}: {messages[j].text}")
        
        context = '\n'.join(context_parts)
        
        windows.append(MessageWindow(
            message_id=msg.id,
            message_text=msg.text,
            context=context,
            sender_id=msg.sender_id,
            timestamp=msg.timestamp,
            is_from_me=msg.is_from_me
        ))
    
    return windows


def create_sample_data() -> Dict:
    """
    Create sample conversation data for testing.
    
    Returns a dict in the expected JSON format.
    """
    return {
        "conversation_id": "sample_conv_001",
        "participants": ["alice", "bob"],
        "messages": [
            {
                "id": "1",
                "sender_id": "alice",
                "text": "hey! are you coming to the party tonight?",
                "timestamp": "2025-01-15T18:00:00Z"
            },
            {
                "id": "2",
                "sender_id": "bob",
                "text": "what party?",
                "timestamp": "2025-01-15T18:02:00Z"
            },
            {
                "id": "3",
                "sender_id": "alice",
                "text": "mike's birthday at his place! starts at 9",
                "timestamp": "2025-01-15T18:02:30Z"
            },
            {
                "id": "4",
                "sender_id": "bob",
                "text": "oh nice, yeah I'll probably swing by",
                "timestamp": "2025-01-15T18:05:00Z"
            },
            {
                "id": "5",
                "sender_id": "alice",
                "text": "awesome! want me to pick you up?",
                "timestamp": "2025-01-15T18:05:45Z"
            },
            {
                "id": "6",
                "sender_id": "bob",
                "text": "nah I'm good, I'll drive myself. thanks tho!",
                "timestamp": "2025-01-15T18:08:00Z"
            },
            {
                "id": "7",
                "sender_id": "alice",
                "text": "sounds good, see you there! 🎉",
                "timestamp": "2025-01-15T18:08:30Z"
            },
            {
                "id": "8",
                "sender_id": "bob", 
                "text": "see ya",
                "timestamp": "2025-01-15T18:10:00Z"
            },
            {
                "id": "9",
                "sender_id": "alice",
                "text": "btw did you finish that project for class?",
                "timestamp": "2025-01-15T19:30:00Z"
            },
            {
                "id": "10",
                "sender_id": "bob",
                "text": "ugh don't remind me 😩 still have like 3 more pages to write",
                "timestamp": "2025-01-15T19:35:00Z"
            },
            {
                "id": "11",
                "sender_id": "alice",
                "text": "lol same, I've been procrastinating all week",
                "timestamp": "2025-01-15T19:36:00Z"
            },
            {
                "id": "12",
                "sender_id": "bob",
                "text": "we should have a study sesh tomorrow",
                "timestamp": "2025-01-15T19:38:00Z"
            },
            {
                "id": "13",
                "sender_id": "alice",
                "text": "yes!! library at 2?",
                "timestamp": "2025-01-15T19:38:30Z"
            },
            {
                "id": "14",
                "sender_id": "bob",
                "text": "perfect, I'll bring coffee",
                "timestamp": "2025-01-15T19:40:00Z"
            },
            {
                "id": "15",
                "sender_id": "alice",
                "text": "you're the best 💕",
                "timestamp": "2025-01-15T19:40:30Z"
            }
        ]
    }


# Quick test when run directly
if __name__ == "__main__":
    # Test with sample data
    sample = create_sample_data()
    parser = JSONParser(my_user_id="alice")
    messages = parser.parse_data(sample)
    
    print(f"Parsed {len(messages)} messages")
    print("\nFirst 3 messages:")
    for msg in messages[:3]:
        print(f"  [{msg.sender_id}]: {msg.text}")
    
    # Create windows
    windows = create_message_windows(messages, window_size=2)
    
    print(f"\nCreated {len(windows)} message windows")
    print("\nExample window (message 4):")
    print(windows[3].context)
