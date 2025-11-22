#--------- Embed messages with OpenAI's API ---------------

from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def create_embedding(text):
    """
    Convert text to a vector embedding.
    Returns a list of 1536 floats.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

#-------------------Embed messages with context---------------------------------------
"""The message "sure" by itself tells us nothing. But "sure" in response 
to "want to hang out tomorrow?" tells us the user agrees to plans casually.
So we create embeddings for message windows: """

def create_message_windows(messages, window_size=3):
    """
    Create context windows around each message.
    
    For the message "sure", we might create:
    "A: want to hang out tomorrow? B: sure"
    
    This captures the conversational context.
    """
    windows = []
    
    for i, msg in enumerate(messages):
        # Get surrounding messages for context
        start = max(0, i - window_size)
        end = min(len(messages), i + window_size + 1)
        
        # Build the context string
        context_parts = []
        for j in range(start, end):
            sender_label = "Me" if messages[j]['is_from_me'] else "Them"
            context_parts.append(f"{sender_label}: {messages[j]['text']}")
        
        windows.append({
            'message_id': msg['id'],
            'message_text': msg['text'],
            'context': '\n'.join(context_parts),
            'sender': msg['sender'],
            'timestamp': msg['timestamp'],
            'is_from_me': msg['is_from_me']
        })
    
    return windows