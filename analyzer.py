import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class TranscriptAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
        self.client = genai.Client(api_key=api_key)

    def analyze(self, transcript: str) -> dict:
        """
        Analyzes the call transcript and returns the outcome and summary.
        
        Args:
            transcript: The text of the call transcript.
            
        Returns:
            A dictionary with 'outcome' (YES/NO), 'summary' (short reason), and 'client_name' (str).
        """
        prompt = f"""
        Analyze the following call transcript. 
        Determine if the client said "YES" (interested/moving forward) or "NO" (not interested/declined).
        Also, extract the core reason for the "YES" or "NO" as a short summary.
        Finally, extract the client's name from the context of the conversation. If you absolutely cannot determine the name, use "Client".
        Also attempt to extract the client's email address if they mention it during the call. If not mentioned, return an empty string "".

        Return the result as a JSON object with exactly these four keys:
        - "outcome": either "YES" or "NO"
        - "summary": a short string explaining the core reason.
        - "client_name": the extracted name of the client.
        - "client_email": the extracted email address or "".

        Transcript:
        {transcript}
        """

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        try:
            result = json.loads(response.text)
            # Ensure the outcome is strictly YES or NO
            if result.get("outcome") not in ["YES", "NO"]:
                if "yes" in str(result.get("outcome")).lower():
                    result["outcome"] = "YES"
                else:
                    result["outcome"] = "NO"
            return result
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON from response: {response.text}")

# Example usage (for testing)
if __name__ == "__main__":
    try:
        analyzer = TranscriptAnalyzer()
        sample_transcript = "Client: I think this sounds great, let's move forward with the plan. Agent: Awesome, I will send the contract."
        print(f"Testing transcript: {sample_transcript}")
        result = analyzer.analyze(sample_transcript)
        print(f"Analysis Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
