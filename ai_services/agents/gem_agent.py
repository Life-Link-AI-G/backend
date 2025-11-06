import os
import json
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from mimic_human import get_instant_health_snapshot, UserProfile, Activity


def create_gemini_agent(sample: str, api_key: str) -> str:
    """Call the Gemini LLM to get a cardiac arrest risk score between 0 and 1.

    Args:
        sample: JSON string or text containing the user health data
        api_key: API key for Google Generative AI

    Returns:
        The model's response content (expected to be a floating number between 0 and 1)
    """
    template = f"""
You are an expert Health Analyst.
Based on the following user health data provide the risk score of cardiac arrest on a scale of 0-1 where 0 means no risk and 1 means high risk.
Return a JSON with two keys: "risk" and "short_report".
"risk" must be a float number between 0 and 1.
"short_report" must be a brief (2-3 sentences) explanation of the risk assessment.

User Health Data:
{sample}
"""

    llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash", temperature=0)
    response = llm.invoke(template)
    return response.content


if __name__ == "__main__":
    # Read API key from environment to avoid hardcoding keys in source
    api_key = os.getenv("GOOGLE_API_KEY","AIzaSyCiF_VKTJ2t5TT2JczRHilpoioCQaBChgI")
    if not api_key:
        print("ERROR: please set the GOOGLE_API_KEY environment variable before running this script.")
    else:
        # Build a sample user and generate an instant health snapshot to use as the LLM input
        sample_user = UserProfile(user_id="SAMPLE_001", age=55, gender="M", weight_kg=85, height_cm=175, fitness_level="average")
        sample = get_instant_health_snapshot(sample_user, Activity.STRESSED.value)

        print("Generated sample (from mimic_human):")
        print(sample)

        response_json = create_gemini_agent(sample, api_key)
        # The response may contain markdown, so we need to extract the JSON part
        start = response_json.find('```json')
        if start != -1:
            response_json = response_json[start+7:]
            end = response_json.find('```')
            if end != -1:
                response_json = response_json[:end]
        
        data = json.loads(response_json)
        print("Predicted cardiac arrest risk:", data["risk"])
        print("Short report:", data["short_report"])