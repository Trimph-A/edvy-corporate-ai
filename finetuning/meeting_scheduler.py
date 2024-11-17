import requests
from langchain.llms.base import LLM
from langchain_core.runnables import Runnable
from langchain.prompts import PromptTemplate  
from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType
from .utils import load_config
from schedule_manager.calendar_service import check_availability, schedule_meeting_event, check_group_availability


# Load configuration for Watsonx
config = load_config('config/config.yaml')

WATSONX_API_URL = f"https://{config['watsonx']['region']}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
WATSONX_API_KEY = config['watsonx']['api_key']
WATSONX_PROJECT_ID = config['watsonx']['project_id']
WATSONX_MODEL_ID = config['watsonx']['model_id']


def process_query_with_watsonx(user_input: str) -> str:
    """
    Send a user query to the Watsonx API and return the model's response.
    """
    payload = {
        "input": user_input,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 300,
            "repetition_penalty": 1.1,
        },
        "model_id": WATSONX_MODEL_ID,
        "project_id": WATSONX_PROJECT_ID,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WATSONX_API_KEY}",
    }

    try:
        response = requests.post(WATSONX_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [{}])[0].get("generated_text", "")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error communicating with Watsonx API: {str(e)}")


# LangChain integration with Watsonx LLM
class WatsonxLLM(LLM, Runnable):
    """
    Wrapper for IBM Watsonx model for use in LangChain.
    """

    def __init__(self):
        super().__init__()

    def _generate(self, prompt: str, stop: list = None) -> str:
        """
        Generate text using the Watsonx API by sending the prompt and getting the result.
        """
        return process_query_with_watsonx(prompt)

    @property
    def _llm_type(self) -> str:
        """
        Return the type of the LLM.
        """
        return "Watsonx"

    def _call(self, prompt: str) -> str:
        """
        Call the LLM to process the query using the Watsonx API.
        """
        return self._generate(prompt)


# LangChain initialization
llm = WatsonxLLM()

# Sample Prompt Template
prompt_template = PromptTemplate(
    input_variables=["user_input"],
    template="""
    You are a virtual assistant. Your job is to assist the user in scheduling meetings.

    - If the user wants to schedule a meeting, check their availability and their group's availability.
    - Suggest an appropriate time if the preferred date and duration are unavailable.
    - Provide detailed responses with actions you plan to take.

    User query: {user_input}
    """
)

# Tools for LangChain agent
tools = [
    Tool(
        name="check_availability",
        func=check_availability,
        description="Check if a user is available for a specific time slot."
    ),
    Tool(
        name="schedule_meeting_event",
        func=schedule_meeting_event,
        description="Schedule a meeting with one or more users."
    ),
    Tool(
        name="check_group_availability",
        func=check_group_availability,
        description="Check if all members of a group are available for a given time slot."
    )
]

# Initialize LangChain agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
