import base64
import requests
import os

class VisionEngine:
    def __init__(self):
        # Default Ollama local endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
        self.vision_model = "llava"

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Reads an image file and converts it to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def describe_image(self, image_path: str) -> str:
        """
        Sends the base64 image to Llava with a strict prompt to return 
        a caption and exactly 3 tags, as per assignment requirements.
        """
        if not os.path.exists(image_path):
            return "❌ Error: Could not locate the downloaded image on the server."

        try:
            base64_image = self._encode_image_to_base64(image_path)
        except Exception as e:
            return f"❌ Error processing image file: {e}"

        prompt = (
            "Analyze this image. You must provide exactly two things:\n"
            "1. A short, one-sentence caption describing the main subject.\n"
            "2. Exactly 3 keywords or tags related to the image.\n\n"
            "Format your response EXACTLY like this:\n"
            "📸 Caption: [Your caption here]\n"
            "🏷️ Tags: #tag1, #tag2, #tag3"
        )

        payload = {
            "model": self.vision_model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False
        }
        
        try:
            print(f"Sending image to {self.vision_model}...")
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            result_text = response.json().get("response", "").strip()
            return result_text
            
        except requests.exceptions.RequestException as e:
            return (f"❌ Error connecting to Ollama: {e}\n"
                    f"Make sure Ollama is running and you have run 'ollama pull {self.vision_model}'.")