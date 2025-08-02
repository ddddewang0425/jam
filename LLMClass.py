from openai import OpenAI
import base64
import requests
import firebase_admin
from firebase_admin import credentials, storage
import uuid
import os
import json
import config
def encode_image_to_base64(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string
if not firebase_admin._apps:
    cred = credentials.Certificate(config.get_firebase())
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'jams-f92b1.firebasestorage.app'
    })
else:
    print("Here~!")
    app = firebase_admin.get_app()
    print(app.options.get('storageBucket', 'No storage bucket found'))
class ImageUploader:
    def __init__(self):
        pass
    def upload_to_firebase(self, image_path, myuuid):
        bucket = storage.bucket()
        blob = bucket.blob(f"uploads/{myuuid}/{uuid.uuid4()}{os.path.splitext(image_path)[1]}")
        blob.upload_from_filename(image_path)
        blob.make_public()
        return blob.public_url

class LLMChatBot:
    def __init__(self, model_name="gpt-4o", temperature=0.4, key=None, uuid=None):
        self.img_uploader = ImageUploader()
        self.model_name = model_name
        self.temperature = temperature
        self.messages = []
        assert key is not None, "API key must be provided"
        assert uuid is not None, "UUID must be provided"
        self.client = OpenAI(
            api_key=key
        )
        self.uuid = uuid
        print("LLMChatBot is initialized with model:", self.model_name)

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def add_message_front(self, role, content):
        if len(self.messages) == 0:
            self.messages.append({"role": role, "content": content})
        else:
            self.messages.insert(0, {"role": role, "content": content})
    
    def pop_message(self):
        if self.messages:
            return self.messages.pop()
        return None
    
    def pop_message_front(self):
        if self.messages:
            return self.messages.pop(0)
        return None

    def have_system_prompt(self):
        if len(self.messages)>0:
            return self.messages[0]['role'] == 'system'
        return False
    
    def clear_messages(self):
        self.messages = []

    def get_response(self, query, store=True):
        if store:
            self.add_message("user",query)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature,
        )
        if store:
            self.add_message("assistant", response.choices[0].message.content)
        return response.choices[0].message.content
    
    def get_response_vision(self, query, image_path, text_store=True, image_store=False):
        image_url = self.img_uploader.upload_to_firebase(image_path, self.uuid)
        # image_b64 = encode_image_to_base64(image_path)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages[0:] + [{
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ], 
                }], 
            temperature=self.temperature,
        )
        if image_store:
            self.add_message("user",[
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ])
            self.add_message("assistant", response.choices[0].message.content)
        elif text_store:
            self.add_message("user", query)
            self.add_message("assistant", response.choices[0].message.content)

        return response.choices[0].message.content

class ChefBot(LLMChatBot):
    def __init__(self, model_name="gpt-4o", temperature=0.4, key=None, uuid=None, system_prompt_path="ChefBotSystemPrompt.txt"):
        super().__init__(model_name, temperature, key, uuid)
        self.init_system_prompt(system_prompt_path)

    def init_system_prompt(self, system_prompt_path):
        if self.have_system_prompt():
            self.pop_message_front()
        self.add_message_front("system",open(system_prompt_path, "r").read())

    def get_response_realtime_vision(self, query, image_path="vision.png", text_store=True, image_store=False):
        """
        The parameters:
            - image_path: needed to be updated with the precise image name.
        """

        return self.get_response_vision(query, image_path, text_store, image_store)