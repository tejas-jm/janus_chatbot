from core.rag_engine import RAGEngine
from core.vision_engine import VisionEngine
from core.cache_manager import CacheManager
from core.state_manager import add_to_history, get_history

# Initialize our engines and cache once when the module loads
rag = RAGEngine()
vision = VisionEngine()
cache = CacheManager()

async def handle_ask_command(platform: str, user_id: str, query: str) -> str:
    """
    Handles text queries for the RAG system.
    """
    unique_user_id = f"{platform}_{user_id}"
    
    # 1. Check Cache (Fast Path)
    cached_response = cache.get(query)
    if cached_response:
        # We still want to log this interaction in the history!
        add_to_history(unique_user_id, f"User: {query}")
        add_to_history(unique_user_id, f"Bot: {cached_response}")
        return f"⚡ (Cached)\n{cached_response}"

    # 2. Retrieve Conversation History
    history = get_history(unique_user_id)
    
    # 3. RAG Retrieval
    context_chunks, sources = rag.retrieve(query)
    
    # 4. Generate Answer via LLM
    answer = rag.generate_answer(query, context_chunks, history)
    
    # 5. Format Output with Source Snippets
    if sources:
        final_response = f"{answer}\n\n📝 Sources: {', '.join(sources)}"
    else:
        final_response = answer
    
    # 6. Update State & Cache (Slow Path)
    add_to_history(unique_user_id, f"User: {query}")
    # We log just the answer to history (excluding the sources string for cleaner context)
    add_to_history(unique_user_id, f"Bot: {answer}")
    cache.set(query, final_response)
    
    return final_response

async def handle_image_upload(platform: str, user_id: str, image_path: str) -> str:
    """
    Handles image uploads for the Vision system.
    """
    unique_user_id = f"{platform}_{user_id}"
    
    # Log the image upload to history so the summarizer knows it happened
    add_to_history(unique_user_id, "User: [Uploaded an Image]")
    
    # Process the image via Llava
    response = vision.describe_image(image_path)
    
    # Log the result to history
    add_to_history(unique_user_id, f"Bot: [Image Analysis] {response}")
    
    return response

async def handle_summarize_command(platform: str, user_id: str) -> str:
    """
    Handles the /summarize command by passing history to the LLM.
    """
    unique_user_id = f"{platform}_{user_id}"
    history = get_history(unique_user_id)
    
    if not history:
        return "We haven't chatted enough for me to summarize anything yet!"
        
    summary = rag.summarize_text(history)
    return f"Here is a summary of our chat:\n\n{summary}"