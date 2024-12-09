from openai import OpenAI
import logging
import json
from typing import Dict
from ai2aidemo.core.schema import CharacterProfile, RolePlayInput

class TextParser:
    def __init__(self):
        self.client = OpenAI()
    
    def parse_roleplay_to_profile(self, role_input: RolePlayInput) -> CharacterProfile:
        """Convert role play text input into a character profile"""
        
        prompt = f"""
        Based on this character description, create a detailed profile:
        
        Name: {role_input.name}
        Description: {role_input.description}
        Personality: {role_input.personality or 'Not specified'}
        
        Extract and organize the information into a JSON object with these EXACT fields:
        {{
            "name": "{role_input.name}",
            "background": "concise background summary",
            "interests": ["topic1", "topic2", ...],
            "knowledge_areas": ["area1", "area2", ...],
            "personality": "{role_input.personality or 'Not specified'}"
        }}

        IMPORTANT:
        1. Return ONLY the JSON object, no other text
        2. Ensure valid JSON format
        3. Make reasonable inferences from the description
        4. Keep lists non-empty (at least one item)
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at analyzing character descriptions. Output only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Get the response text and ensure it's clean JSON
            response_text = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse the JSON string
            try:
                profile_dict = json.loads(response_text)
                parsed_profile = CharacterProfile(**profile_dict)
                return parsed_profile
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error: {str(e)}\nResponse text: {response_text}")
                raise ValueError(f"Invalid JSON in response: {str(e)}")
            except Exception as e:
                logging.error(f"Profile validation error: {str(e)}\nProfile dict: {profile_dict}")
                raise ValueError(f"Invalid profile structure: {str(e)}")
            
        except Exception as e:
            logging.error(f"Error parsing character description: {str(e)}")
            raise ValueError(f"Failed to parse character input: {str(e)}") 