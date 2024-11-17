import yaml
import requests

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('config/config.yaml')

ibm_api_key = config['ibm']['api_key']
ibm_service_url = config['ibm']['service_url']

def generate_alternative_suggestion(preferred_dates, working_hours):
    """
    Generates alternative suggestions for meeting times using IBM Watsonx or similar AI service,
    considering working hours.
    """
    # Construct a natural language prompt based on failed attempts, preferred dates, and working hours
    prompt = (
        f"The following meeting dates were unavailable: {', '.join([str(date) for date in preferred_dates])}. "
        f"The working hours are from {working_hours['start']} to {working_hours['end']}. "
        "Suggest alternative time slots within the next week that fall within the working hours "
        "and might work for all attendees."
    )

    headers = {
        'Authorization': f'Bearer {ibm_api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        "input": prompt,
        "model_id": "your-model-id",  # Replace with Watsonx model ID if required
        "options": {
            "top_k": 5,
            "max_tokens": 100
        }
    }

    response = requests.post(f"{ibm_service_url}/v1/generate", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        # Extract the suggestion text
        return result.get('text', "No suggestion available at this time.")
    else:
        # Handle errors
        raise Exception(f"Failed to generate suggestion: {response.status_code} {response.text}")
