from src.ui_core.db import get_conn, init_db
from src.ui_core.prompts_repo import update_prompt

def add_default_prompts():
    """Add default prompts to the database."""
    conn = get_conn()
    try:
        # Default system prompt
        update_prompt(
            conn,
            name="system_prompt",
            prompt="""You are a helpful AI assistant that provides accurate and concise information.
            Be polite and professional in your responses.""",
            meta={"type": "system", "version": "1.0"}
        )
        
        # Default chat prompt
        update_prompt(
            conn,
            name="chat_prompt",
            prompt="""You are having a conversation with a user. 
            Respond to their messages in a friendly and helpful manner.""",
            meta={"type": "chat", "version": "1.0"}
        )
        
        # Default cardset prompt
        update_prompt(
            conn,
            name="cardset_prompt",
            prompt="""You are a helpful assistant that creates interactive cardsets based on user queries. 
            Generate relevant questions to gather more information.""",
            meta={"type": "cardset", "version": "1.0"}
        )
        
        print("Successfully added default prompts to the database.")
        
    except Exception as e:
        print(f"Error adding default prompts: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Initialize the database and create tables
    init_db()
    # Add default prompts
    add_default_prompts()
