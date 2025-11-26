import json
from vertexai import agent_engines
import json
import re

def process_agent_response(raw_response):
    """
    Process agent response:
      - If JSON (with or without ```json) → return dict
      - Otherwise return dict with 'message' key
    """
    try:
        # If response is a string containing JSON markdown
        if isinstance(raw_response, str) and "```json" in raw_response:
            cleaned_text = re.sub(r'^.*?```json', '', raw_response, flags=re.DOTALL)
            cleaned_text = re.sub(r'```$', '', cleaned_text.strip())
            parsed = json.loads(cleaned_text)
            return parsed if isinstance(parsed, dict) else {"message": str(parsed)}
        # If response is a string that is plain JSON
        if isinstance(raw_response, str):
            raw_response = raw_response.strip()
            try:
                parsed = json.loads(raw_response)
                return parsed if isinstance(parsed, dict) else {"message": str(parsed)}
            except json.JSONDecodeError:
                return {"message": raw_response}
        # If already a dict, return as-is
        if isinstance(raw_response, dict):
            return raw_response
        # Otherwise, fallback
        return {"message": str(raw_response)}
    except Exception as e:
        print("Error while processing agent response:", e)
        return {"message": str(raw_response)}

def agent_engine_caller_with_session(user_content, agent_path, session_id: str, user_id: str = "userabc"):
    print(f"Inside agent_engine_caller_with_session user_content => {user_content}")
    current_session_id = ""
    agent_response = ""
    
    agent_engine = agent_engines.get(agent_path)
    
    if not session_id:
        session = agent_engine.create_session(user_id=user_id)
        print(f"Inside agent_engine_caller_with_session session => {session}")
        current_session_id = session["id"]
    else:
        current_session_id = session_id

    for event in agent_engine.stream_query(
        user_id=user_id, session_id=current_session_id, message=user_content
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                print(f"Inside agent_engine_caller part => {part}")
                if "text" in part:
                    agent_response = part["text"]
    
    print(f"Inside agent_engine_caller response => {agent_response}")
    
    # Process the response and merge with session_id
    parsed_response = process_agent_response(agent_response)
    print(f"Inside agent_engine_caller parsed_response => {parsed_response}")
    
    # Merge parsed_response directly with session_id (no extra nesting)
    final_response = {**parsed_response, "session_id": current_session_id}
    print(f"Inside agent_engine_caller final_response => {final_response}")

    return final_response

def agent_engine_caller(user_content, agent_path, user_id: str = "userabc"):
    print(f"Inside agent_engine_caller user_content => {user_content}")
    agent_engine = agent_engines.get(
        agent_path
    )
    session = agent_engine.create_session(user_id=user_id)
    print(f"Inside agent_engine_caller session => {session}")

    response = ""
    for event in agent_engine.stream_query(
        user_id=user_id, session_id=session["id"], message=user_content
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response = part["text"]
    print(f"Inside agent_engine_caller response => {response}")
    parsed_response = process_agent_response(response)
    print(f"Inside agent_engine_caller parsed_response => {parsed_response}")
    return parsed_response