import requests
import json

class OpenAIChatClient:
    def __init__(self, server_ip):
        self.server_ip = server_ip

    def simple_chat(self, prompt):
        try:
            response = self._send_request(prompt)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error: {e}")
            return None

    def multi_turn_chat(self, new_message, history):
        messages = history + [{"role": "user", "content": new_message}]
        response = self._send_request(json.dumps({"model": "Qwen/Qwen2.5-1.5B-Instruct", "messages": messages, "max_completion_tokens": 1024, "stream": False, "stream_options": {"include_usage": False}, "temperature": 0.7, "top_p": 1, "store": False}))
        return response.json()['choices'][0]['message']['content'], messages

    def full_chat(self, messages, options):
        response = self._send_request(json.dumps({"model": "Qwen/Qwen2.5-1.5B-Instruct", "messages": messages, "max_completion_tokens": 1024, "stream": False, "stream_options": {"include_usage": False}, "temperature": 0.7, "top_p": 1, "store": False}))
        return response.json()

    def _send_request(self, data):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{self.server_ip}/api/v1/chat/completions", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")
        return response.json()

# Usage examples
if __name__ == "__main__":
    client = OpenAIChatClient(server_ip="http://localhost:8000")
    print(client.simple_chat("hello"))
    print(client.multi_turn_chat("hello", [{"role": "system", "content": "Follow instructions strictly."}]))
    print(client.full_chat([{"role": "system", "content": "Follow instructions strictly."}, {"role": "user", "content": "hello"}], {"max_completion_tokens": 1024, "stream": False, "stream_options": {"include_usage": False}, "temperature": 0.7, "top_p": 1, "store": False}))