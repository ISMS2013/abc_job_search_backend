import json
from agent_engine_caller import *
from google.genai.types import HttpOptions, Part,Content, Blob
from config import project_config

agent_path = project_config.get("engine_id4")


def agent_caller(data : dict):
    result = {}
    print(f"Inside agent_caller with input data {data}")
    message = data.get("message", "")
    session_id = data.get("session_id", "")
    user_id = data.get("user_id", "")
    user_content = Content(
            role="user",
            parts=[
                Part(
                    text=(
                        message
                    )
                )
                # ,Part(
                #     text=( 
                    
                #         json.dumps(description_details).encode("utf-8")
                        
                #     )
                # )
            ]
        )
    result = agent_engine_caller(user_content=message, agent_path=agent_path, session_id=session_id, user_id=user_id)
    # return {
    #     "user_id": user_id,
    #     "session_id": session_id,
    #     "agent_response": f"Echo: {message}"
    # }
    return result

def agent_caller_json(data : dict):
    result = {}
    print(f"Inside agent_caller_json with input data {data}")
    session_id = data.get("session_id", "")
    # user_id = data.get("user_id", "")
    # The agent engine expects a string message. We serialize the dict to a JSON string.
    user_content = json.dumps(data)
    result = agent_engine_caller(user_content=user_content, agent_path=agent_path, session_id=session_id)
    # return {
    #     "user_id": user_id,
    #     "session_id": session_id,
    #     "agent_response": f"Echo: {message}"
    # }
    return result


def agent_caller_generic(data : dict, agent_path : str):
    result = {}
    print(f"Inside agent_caller with input data {data}")
    message = data.get("message", "")
    session_id = data.get("session_id", "")
    user_id = data.get("user_id", "")
    result = agent_engine_caller_generic(user_content=message, agent_path=agent_path, session_id=session_id, user_id=user_id)
    return result