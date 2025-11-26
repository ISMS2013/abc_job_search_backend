from google.cloud import firestore
import asyncio
import copy
from config import project_config

PROJECT_ID = project_config.get('project_id')
DATABASE_ID = [FIRESTORE_DATABASE_NAME]
COLLECTION_NAME = [FIRESTOR_COLLECTION_NAME]

db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)
print(f"database_operations db=> {db}")

def upload_job_opport_to_firestore(job_opport_data, input_key: str) -> None:
    """
    Uploads the generated job opportunity data to the Firestore cache.
    Uses the unique input_key (the job domain, e.g., 'WELDER') as the document ID.
    
    Args:
        job_opport_data: The dictionary containing the agent's full response (the list of 10 jobs).
        input_key: The unique string representing the job domain (e.g., 'WELDER').
    """
    if db is None:
        print("Caching skipped: Firestore client is not initialized.")
        return

    if not job_opport_data:
        raise ValueError("job_opport data is empty.")
    
    # Use the input_key (domain, e.g., "WELDER") as the Firestore document ID
    doc_ref = db.collection(COLLECTION_NAME).document(input_key)
    
    try:
        # Uploads the entire JSON structure to the document named by input_key
        doc_ref.set(job_opport_data)
        print(f"Successfully uploaded cache data for input: '{input_key}' to Firestore.")
    except Exception as e:
        print(f"Error uploading job_opport cache to Firestore for input '{input_key}': {e}")


def fetch_job_opport_from_cache(input_key: str):
    """
    Attempts to retrieve a job opportunity document from the Firestore cache 
    using the input_key (job domain) as the document ID.
    
    Args:
        input_key: The unique string representing the job domain (e.g., 'WELDER').
        
    Returns:
        The job opportunities dictionary if found, otherwise None.
    """
    if db is None:
        print("Cache check skipped: Firestore client is not initialized.")
        return None

    print(f"--- Entering fetch_job_opport_from_cache for key: {input_key} ---")
    try:
        # Get reference using the input_key (domain)
        doc_ref = db.collection(COLLECTION_NAME).document(input_key)
        
        # Fetch the document
        doc = doc_ref.get()
        
        if doc and doc.exists:
            job_opport_output = doc.to_dict()
            print(f"Cache hit: Job opportunity found for key '{input_key}'.")
            return job_opport_output
        else:
            print(f"Cache miss: Document not found for key '{input_key}'.")
            return None 
            
    except Exception as e:
        print(f"Firestore READ error for key '{input_key}': {e}")
        return None 
    finally:
        print("--- Exiting fetch_job_opport_from_cache ---")

# # get_job_opport
# def fetch_job_opport_from_cache(jobs: str) -> dict | None:
#     """
#     Attempts to retrieve a job_opport document from Firestore cache using the 
#     exact jobs string as the document ID.

#     Returns:
#         The job_opport dictionary (including injected email_id) if found, otherwise None.
#     """
#     print(f"--- Entering fetch_job_opport_from_cache for jobs: {jobs} ---")
#     try:
#         doc_ref = db.collection("jobs_opportunities").document(jobs)
#         print(f"job_opport_fetch_cache doc_ref => {doc_ref}")
        
#         doc = doc_ref.get()
#         print(f"job_opport_fetch_cache doc => {doc}")
#         if doc and doc.exists:
#             job_opport_output = doc.to_dict()
#             print(f"job_opport_fetch_cache job_opport found in cache.")
#             return job_opport_output
#         else:
#             print(f"job_opport_fetch_cache Cache miss: Document not found.")
#             return None            
#     except Exception as e:
#         print(f"job_opport_fetch_cache Firestore READ error: {e}")
#         return None 
#     finally:
#         print("--- Exiting fetch_job_opport_from_cache ---")