def get_greeting() -> str:
    """A UI-agnostic function that represents a piece of core business logic.
    
    Returns:
        str: A greeting message from the core engine.
    """
    return "Hello from neurocli_core The engine is running."

def get_ai_response(prompt: str) -> str:
    """Simulates processing a user's prompt and returning an AI-generated response.
    
    Args:
        prompt: The user's input prompt.
        
    Returns:
        A simulated AI response.
    """
    return f"AI Response to '{prompt}': This is a simulated response."