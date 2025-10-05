import requests
import json

class Assistant:
    def __init__(self, model="llama3.1:8b", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url

    def ask_model(self, user_query: str, context: str = "") -> str:
        """
        Send query + context to the Ollama model and return its reply.
        """

        # Build structured RAG-style prompt
        prompt = f"""
        You are a helpful AI assistant.

        Context (from memory database):
        {context if context.strip() else "No relevant past context."}

        User: {user_query}
        Assistant:"""

        try:
            payload = {"model": self.model, "prompt": prompt}
            response = requests.post(self.url, json=payload, stream=True, timeout=60)

            reply = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        reply += data["response"]
                    if data.get("done", False):
                        break

            return reply.strip() if reply else "I didn’t get a response."

        except Exception as e:
            print(f"[ERROR] Assistant failed: {e}")
            return "Sorry, I had trouble responding."
