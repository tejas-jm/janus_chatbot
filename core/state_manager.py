import collections

# Global dictionary to hold the state in memory.
# maxlen=6 keeps exactly 3 interactions (3 User messages + 3 Bot replies).
user_histories = collections.defaultdict(lambda: collections.deque(maxlen=6))

def add_to_history(user_id: str, message: str):
    """
    Appends a message to the user's history.
    
    Args:
        user_id (str): The compound ID (e.g., 'telegram_123456' or 'discord_987654')
        message (str): The formatted message string (e.g., 'User: Hello' or 'Bot: Hi there')
    """
    user_histories[user_id].append(message)

def get_history(user_id: str) -> str:
    """
    Retrieves the user's history and formats it into a single string 
    that can be injected directly into an LLM prompt.
    """
    # If the user hasn't interacted yet, return an empty string
    if user_id not in user_histories or not user_histories[user_id]:
        return ""
    
    # Join the stored messages with newlines
    return "\n".join(user_histories[user_id])

def clear_history(user_id: str):
    """
    Optional utility: Clears the history for a specific user.
    Great if you want to implement a /reset command later.
    """
    if user_id in user_histories:
        user_histories[user_id].clear()