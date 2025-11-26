from flask import Flask, Response, logging, request, jsonify, abort
from google.cloud import storage, firestore
from flask_cors import CORS, cross_origin
import os, json
from database_operations import *
from agent_caller import *
from config import project_config



project_id = project_config.get('project_id')
location= project_config.get('location')
credentials_json_key = project_config.get('credentials_json_key')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_json_key
os.environ.setdefault("GCLOUD_PROJECT", project_id)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CACHE_TYPE'] = 'simple'
db = firestore.Client()


@app.route("/job_opport_generation", methods=["POST"])
def job_opportunities_generation():
    """
    API logic to retrieve job opportunities. Checks Firestore cache first 
    using the 'domain' as the key, then calls the ADK agent if not found.
    """
    print("Inside job_opportunities_generation API")
    try:
        input_data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Invalid JSON input: {str(e)}"}), 400 
    domain = input_data.get("domain") 
    user_id = input_data.get('user_id', 'default_user_id') 

    if not domain:
        return jsonify({
            "error": "Missing 'domain' in the request body. This is used as the unique cache key.", 
            "source": "Validation"
        }), 400
    input_key = domain.upper()
    cached_job_opportunities_output = fetch_job_opport_from_cache(input_key)
    if cached_job_opportunities_output:
        print(f"Jobs found in cache for domain: '{input_key}'. Returning cached data.")
        return jsonify({"result": cached_job_opportunities_output, "source": "Firestore Cache"}), 200

    print(f"Jobs not found in cache. Calling ADK agent for domain: '{domain}'...") 
    agent_payload = {
        "job_title": domain 
    }
    agent_message = json.dumps(agent_payload) 
    agent_path = project_config.get("engine_id")
    try:
        agent_result = agent_engine_caller(
            user_content=agent_message, 
            user_id=user_id,
            agent_path=agent_path)
        
        job_opportunities_data = agent_result
        print("Job opportunities data generated.")
        try:
            upload_job_opport_to_firestore(job_opportunities_data, input_key) 
            print(f"Caching successfully triggered for input: {input_key}")
        except Exception as cache_e:
            print(f"WARNING: Caching failed for input {input_key}: {cache_e}")
            
        return jsonify({"result": job_opportunities_data}), 200

    except Exception as e:
        print(f"An error occurred during agent call or processing: {e}")
        return jsonify({
            "error": f"Failed to generate job opportunities from ADK Agent: {str(e)}", 
            "source": "ADK Agent Failure"
        }), 500
    
@app.route("/job_discover_global", methods=["POST"])
def job_discover_global_api():
    """
    API endpoint to interact with the Job Discovery Agent using a simple text string input.
    Input: Raw text string (the user's message).
    Output: The raw JSON response from the ADK Agent (either a text message or the final schema).
    """
    print("\n--- Inside job_discover_global_api Endpoint ---")
    try:
        input_data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Invalid JSON input: {str(e)}"}), 400 
    user_content = input_data.get("user_input") 
    session_id = input_data.get("session_id") 
    user_id = input_data.get('user_id', 'default_user_id')
    agent_payload = {
        "input_text": user_content 
    }
    agent_message = json.dumps(agent_payload) 
    agent_path = project_config.get("engine_id1")
    try:
        agent_result = agent_engine_caller_with_session(
            user_content=agent_message, 
            user_id=user_id,
            session_id=session_id,
            agent_path=agent_path)
        print("agent_result")
        return jsonify(agent_result), 200

    except Exception as e:
        print(f"An error occurred during agent call: {e}")
        return jsonify({
            "error": f"Failed to communicate with ADK Agent: {str(e)}", 
            "source": "ADK Agent Service"
        }), 500
    
@app.route("/job_apply", methods=["POST"])
def job_apply_api():
    """
    API endpoint to interact with the Job Application Agent using a simple text string input.
    Input: Raw text string (the user's message).
    Output: The raw JSON response from the ADK Agent (either a text message or the final schema).
    """
    print("\n--- Inside job_apply_api Endpoint ---")
    try:
        input_data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Invalid JSON input: {str(e)}"}), 400 
    user_content = input_data.get("user_input") 
    session_id = input_data.get("session_id") 
    user_id = input_data.get('user_id', 'default_user_id')
    agent_payload = {
        "input_text": user_content 
    }
    agent_message = json.dumps(agent_payload) 
    agent_path = project_config.get("engine_id2")
    try:
        agent_result = agent_engine_caller_with_session(
            user_content=agent_message, 
            user_id=user_id,
            session_id=session_id,
            agent_path=agent_path)
        print("agent_result")
        return jsonify(agent_result), 200

    except Exception as e:
        print(f"An error occurred during agent call: {e}")
        return jsonify({
            "error": f"Failed to communicate with ADK Agent: {str(e)}", 
            "source": "ADK Agent Service"
        }), 500
    

@app.route("/interview_scheduler", methods=["POST"])
def job_interview_scheduler_api():
    """
    API endpoint to interact with the interview scheduler Agent using a simple text string input.
    Input: Raw text string (the user's message).
    Output: The raw JSON response from the ADK Agent (either a text message or the final schema).
    """
    print("\n--- Inside job_interview_scheduler_api---")
    try:
        input_data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Invalid JSON input: {str(e)}"}), 400 
    user_content = input_data.get("user_input") 
    session_id = input_data.get("session_id") 
    user_id = input_data.get('user_id', 'default_user_id')
    agent_payload = {
        "input_text": user_content 
    }
    agent_message = json.dumps(agent_payload) 
    agent_path = project_config.get("engine_id3")
    try:
        agent_result = agent_engine_caller_with_session(
            user_content=agent_message, 
            user_id=user_id,
            session_id=session_id,
            agent_path=agent_path)
        print("agent_result:,", agent_result)
        return jsonify(agent_result), 200

    except Exception as e:
        print(f"An error occurred during agent call: {e}")
        return jsonify({
            "error": f"Failed to communicate with ADK Agent: {str(e)}", 
            "source": "ADK Agent Service"
        }), 500
    

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=443)