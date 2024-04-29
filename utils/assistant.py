import os
from os.path import join
import concurrent
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, asdict, replace
import string
import json
import requests
import random
import warnings
from time import sleep

# can use asdict() function to transform dataclass instance into a dict
@dataclass
class RequestParameters:
    model: str = "gpt-4-0125-preview"
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    temperature: float = 0.0
    max_tokens: int = 4096
    top_p: float = 1.0
    stream: bool = False


# The assistant for Azure GPT service
class Assistant():

    def __init__(self, api_key: str, azure_url: str = "http://10.220.5.153:31417/api/", system_prompt: str = "") -> None:
        self.messages = [] # current messages
        self.parameters = RequestParameters()
        self.api_key = api_key
        self.timeout_length = 10
        self.uuid = self.generate_uuid()
        self.last_err_response = None
        self.model_url = azure_url
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def substitute_msg(self, messages: list):
        self.messages = messages

    def set_request_parameters(self, **kwargs):
        self.parameters = replace(self.parameters, **kwargs)

    # @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(30))
    def send_request(self, add_to_msg: bool = True, wait_time=10, max_retry=2, timeout=180) -> str:
        if len(self.messages) > 0:
            last_role = self.messages[-1]["role"]
            if last_role == "assistant":
                warnings.warn("Last message was from assistant as well.")
        url = self.model_url + "requestazuremessage"
        request = asdict(self.parameters)
        request["messages"] = self.messages
        body = {"type": "RequestAzureMessage", "apikey": self.api_key, "request": request, "uuid": {"id": self.uuid}}
        for i in range(max_retry):
            try:
                response_obj = requests.post(url, json=body, timeout=timeout)
            except Exception as e:
                print(f"{i}th try request, exception: {e}")
                if i == max_retry - 1:
                    raise Exception(f"Retry times exceed {max_retry} times, raise exception.")
                sleep(wait_time)
                continue
            if response_obj.status_code == 200:
                response = response_obj.json()
                response_message = response['choices'][0]['message']
                break
            else:
                self.last_err_response = response_obj
                text = response_obj.text
                print(f"{i}th try request error with status code {response_obj.status_code} and text: {text}")
                if '400' in text:
                    warnings.warn("Since this is a 400 error, we finish the dialogue and do not raise exception.")
                    response_message = {'role': 'assistant', 'content': '\\boxed{' + text + '}'}
                    break
                if i == max_retry - 1:
                    raise Exception(f"Retry times exceed {max_retry} times, raise exception.")
                sleep(wait_time)

        if add_to_msg:
            self.messages.append(response_message)

        try:
            content = response_message['content']
        except Exception as e:
            warnings.warn(f"Exception {e} encountered when extract content from the response\n{response_message}")
            content = ""
        return content
    
    def receive_user_prompt(self, user_prompt: str):
        message = {"role": "user", "content": user_prompt}
        self.messages.append(message)
        return

    @staticmethod
    def generate_uuid(length=10):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def reset_dialogue(self, remain_system_prompt=True):
        if self.messages and remain_system_prompt and self.messages[0]["role"] == 'system':
            self.messages = [self.messages[0]]
        else:
            self.messages = []