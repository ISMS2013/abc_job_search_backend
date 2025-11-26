import vertexai
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


def find_last_message(data):
    """
    Recursively searches all occurrences of the key 'message'
    in a nested JSON structure and returns the *last* one found.
    """
    found = []

    def _search(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ("upskill_response", "message"):
                    found.append(value)
                _search(value)
        elif isinstance(obj, list):
            for item in obj:
                _search(item)

    _search(data)
    return found[-1] if found else None




def agent_engine_caller(user_content, agent_path, session_id: str, user_id: str = "userabc"):
    print(f"Inside agent_engine_caller user_content => {user_content}, user_id => {user_id}")
    current_session_id = ""
    agent_response = ""
    final_response = {}
    agent_engine = agent_engines.get(agent_path)
    # Create session if missing
    # 1. Session Management
    if not session_id:
        try:
            session = agent_engine.create_session(user_id=user_id)
            current_session_id = session["id"]
            print(f"Inside agent_engine_caller_quiz session created => {session}")
        except Exception as e:
            print(f"Error creating session: {e}")
            return {"agent_response": {"error": f"Session creation failed: {str(e)}"}, "session_id": "error_session_id"}
    else:
        current_session_id = session_id
    # Stream query to agent
    for event in agent_engine.stream_query(
            user_id=user_id, session_id=current_session_id, message=user_content
    ):
        if "content" in event and "parts" in event["content"]:
            print(f"[CONTENT => {event['content']}")
            for part in event["content"]["parts"]:
                if "text" in part:
                    agent_response = part["text"]
    # print(f"[SESSION] session => {session}")
    print(f"Inside agent_engine_caller raw response => {agent_response}")
    # Always process response to dict
    parsed_response = process_agent_response(agent_response)
    print(f"Inside agent_engine_caller parsed_response => {parsed_response}")
    

    final_response["message"] = find_last_message(parsed_response)
    print(f"[POC] final_response => {final_response}")
    if not final_response.get("message"):
        final_response["message"] = parsed_response
    if "ErrList" in parsed_response:
        final_response["ErrList"] = parsed_response["ErrList"]
    if "show_upload_button" in parsed_response:
        final_response["show_upload_button"] = parsed_response["show_upload_button"]
    final_response["session_id"] = current_session_id
    print(f"Inside agent_engine_caller final_response => {final_response}")
    return final_response

def agent_engine_caller_generic(user_content: str, agent_path: str, session_id: str, user_id: str = "userabc"):
    print(f"Inside agent_engine_caller_quiz user_content => {user_content}")
    current_session_id = ""
    final_response = {}
    
    agent_engine = agent_engines.get(agent_path)
    
    # 1. Session Management
    if not session_id:
        try:
            session = agent_engine.create_session(user_id=user_id)
            current_session_id = session["id"]
            print(f"Inside agent_engine_caller_quiz session created => {session}")
        except Exception as e:
            print(f"Error creating session: {e}")
            return {"agent_response": {"error": f"Session creation failed: {str(e)}"}, "session_id": "error_session_id"}
    else:
        current_session_id = session_id

    stream_output = ""
    try:
        for event in agent_engine.stream_query(
                user_id=user_id, session_id=current_session_id, message=user_content
        ):
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        stream_output += part["text"]
        
    except Exception as e:
        print(f"Error during agent stream_query: {e}")
        return {"agent_response": {"error": f"ADK query failed: {str(e)}"}, "session_id": current_session_id}

    print(f"Inside agent_engine_caller_quiz raw response => {stream_output}")
    
    # 3. Process and Return
    parsed_response = process_agent_response(stream_output)
    print(f"Inside agent_engine_caller_quiz parsed_response => {parsed_response}")
    
    # Return the full quiz data payload and the session ID
    final_response["agent_response"] = parsed_response 
    final_response["session_id"] = current_session_id
    
    # This print statement now shows the correct structure (no 'message': None)
    print(f"Inside agent_engine_caller_quiz final_response => {final_response}") 
    
    return final_response