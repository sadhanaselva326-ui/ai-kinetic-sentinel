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

        def _call_gemini():
            return client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )

        try:
            response = _call_gemini()
        except Exception as rate_err:
            # Retry once after 20s if quota exceeded
            if "429" in str(rate_err) or "RESOURCE_EXHAUSTED" in str(rate_err):
                import time
                time.sleep(20)
                response = _call_gemini()
            else:
                raise

        result_text = response.text
        return json.loads(result_text)

    except Exception as e:
        raise DocumentProcessingError(f"Failed to analyze text using AI: {str(e)}")