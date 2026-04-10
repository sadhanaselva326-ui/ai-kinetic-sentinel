import os
import json
import google.genai as genai
from google.genai import types
from utils.errors import DocumentProcessingError

def analyze_document_text(text: str) -> dict:
    if not text or not text.strip():
        raise DocumentProcessingError("Text is empty or could not be extracted.")
    
    prompt = f"""
    You are an expert AI document analyzer. Given the following document text, perform three tasks:
    1. Summarize the document concisely.
    2. Extract entities: Names, Dates, Organizations, and Monetary Amounts. Extract them as lists of strings.
    3. Determine the overall sentiment of the document. Choose exactly one of: Positive, Neutral, Negative.
    
    Document Text:
    '''
    {text}
    '''
    
    Return your response purely as a JSON object, without any markdown formatting or backticks.
    Use this exact JSON schema:
    {{
        "summary": "string",
        "entities": {{
            "names": ["string"],
            "dates": ["string"],
            "organizations": ["string"],
            "amounts": ["string"]
        }},
        "sentiment": "Positive" | "Neutral" | "Negative"
    }}
    """

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env")

        client = genai.Client(api_key=api_key)

        # Define the AI call logic
        def _call_gemini(model_name):
            return client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )

        # Retry logic: Try 2.0-flash, then retry 2.0-flash, then fallback to 1.5-flash
        attempts = [
            ("gemini-2.0-flash", 0),  # Attempt 1: Fast model
            ("gemini-2.0-flash", 10), # Attempt 2: Re-try after 10s wait
            ("gemini-1.5-flash", 0)   # Attempt 3: Fallback model
        ]

        import time
        response = None
        last_error = None

        for model, delay in attempts:
            if delay > 0:
                time.sleep(delay)
            try:
                response = _call_gemini(model)
                break # Success!
            except Exception as rate_err:
                last_error = rate_err
                # Only retry on rate limits or 503 unavailable
                if "429" in str(rate_err) or "RESOURCE_EXHAUSTED" in str(rate_err) or "503" in str(rate_err) or "UNAVAILABLE" in str(rate_err):
                    continue
                else:
                    raise # If it's a structural error, fail immediately

        if not response:
            raise last_error # Raise the final error if all 3 attempts failed

        result_text = response.text
        return json.loads(result_text)

    except Exception as e:
        raise DocumentProcessingError(f"Failed to analyze text using AI: {str(e)}")