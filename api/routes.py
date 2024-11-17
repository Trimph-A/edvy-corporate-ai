from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import datetime

from finetuning.meeting_scheduler import llm, process_query_with_watsonx

# Creating a router for API endpoints
router = APIRouter()

# Defining the data model for user requests
class UserRequest(BaseModel):
    user_input: str  # The input query provided by the user
    duration: int  # Duration of the meeting in minutes

@router.post("/process-user-query")
async def process_user_query(request: UserRequest, conversation_history: List[Dict[str, str]]):
    """
    Endpoint for processing user queries.
    
    This endpoint determines if a query is related to scheduling a meeting. 
    If so, it uses the Watsonx model to analyze the entire conversation history to infer
    preferred meeting dates and times. For non-meeting-related queries, it processes
    the input and determines if it relates to company policies or provides a generic response.

    Args:
        request (UserRequest): The data model containing the user's query.
        conversation_history (List[Dict[str, str]]): The conversation context as a list of messages.

    Returns:
        dict: The system's response based on the type of query.
    """
    try:
        # Create a prompt to verify if the query is related to scheduling a meeting
        user_prompt = f"""
        Is the following user query related to scheduling a meeting? Respond with "Yes" or "No".
        Query: {request.user_input}
        """
        # Classify the query type using Watsonx
        is_meeting_related = process_query_with_watsonx(user_prompt).strip().lower() == "yes"

        if is_meeting_related:
            # Generate a detailed prompt to analyze the entire conversation history
            conversation_context = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in conversation_history]
            )
            detailed_prompt = f"""
            The user wants to schedule a meeting. Based on the following conversation history, infer:
            1. The user's preferred dates and times.
            2. Any other participants and their availability.
            3. Suggested meeting times if conflicts arise.

            Conversation history:
            {conversation_context}

            Query: {request.user_input}
            """
            # Process the meeting scheduling logic with Watsonx
            meeting_response = process_query_with_watsonx(detailed_prompt)
            return {"response": meeting_response}
        else:
            # Process non-meeting-related queries
            if "company policy" in request.user_input.lower() or "about the company" in request.user_input.lower():
                # Ask a question about the company
                return {"response": ask_about_company(request.user_input)}
            else:
                # Generic fallback response
                generic_response = process_query_with_watsonx(request.user_input)
                return {"response": generic_response}

    except Exception as e:
        # Error handling and returning an HTTP 500 response in case of failure
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")

def ask_about_company(query: str) -> str:
    """
    Processes questions related to the company's policies, goals, or general information.

    Args:
        query (str): The user's question.

    Returns:
        str: The generated response from the trained model.
    """
    if 'trained_chain' not in globals():
        raise HTTPException(status_code=400, detail="Model not trained. Upload documents first.")
    
    try:
        response = trained_chain.run(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate a response: {str(e)}")
