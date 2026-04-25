# SDK Documentation

## Overview
This SDK provides a basic interface for interacting with an OpenAI chat client.

## Installation
```bash
pip install [package-name]
Note: Package name not specified in source code.
```

Quick Start
```python
# Create an instance of the OpenAIChatClient
client = OpenAIChatClient(server_ip="localhost")

# Perform a simple chat
client.simple_chat(prompt="Hello, how are you?")

# Perform a multi-turn chat
client.multi_turn_chat(new_message="I'm good, thanks.", history=[])

# Perform a full chat
client.full_chat(messages=[], options={})
```

Class Reference
### Class: OpenAIChatClient

This class provides methods for interacting with an OpenAI chat client.

### Method: __init__

Initializes the OpenAIChatClient instance.

Method: __init__
Description: Not specified
Parameters:

Name	Type	Required	Description
server_ip	Not specified	True	Required

Returns: Not specified

### Method: simple_chat

Performs a simple chat with the OpenAI chat client.

Method: simple_chat
Description: Not specified
Parameters:

Name	Type	Required	Description
prompt	Not specified	True	Required

Returns: Not specified

### Method: multi_turn_chat

Performs a multi-turn chat with the OpenAI chat client.

Method: multi_turn_chat
Description: Not specified
Parameters:

Name	Type	Required	Description
new_message	Not specified	True	Required
history	Not specified	True	Required

Returns: Not specified

### Method: full_chat

Performs a full chat with the OpenAI chat client.

Method: full_chat
Description: Not specified
Parameters:

Name	Type	Required	Description
messages	Not specified	True	Required
options	Not specified	True	Required

Returns: Not specified

### Method: _send_request

Sends a request to the OpenAI chat client.

Method: _send_request
Description: Not specified
Parameters:

Name	Type	Required	Description
data	Not specified	True	Required

Returns: Not specified

---

## Additional Usage Examples

### Example 1: Simple Chat

```python
# Create an instance of the OpenAIChatClient
client = OpenAIChatClient(server_ip="localhost")

try:
 # Perform a simple chat
 client.simple_chat(prompt="Hello, how are you?")
except Exception as e:
 print(f"Error: {e}")
```

### Example 2: Multi-Turn Chat

```python
# Create an instance of the OpenAIChatClient
client = OpenAIChatClient(server_ip="localhost")

try:
 # Perform a multi-turn chat
 client.multi_turn_chat(new_message="I'm good, thanks.", history=[])
except Exception as e:
 print(f"Error: {e}")
```

### Example 3: Full Chat

```python
# Create an instance of the OpenAIChatClient
client = OpenAIChatClient(server_ip="localhost")

try:
 # Perform a full chat
 client.full_chat(messages=[], options={})
except Exception as e:
 print(f"Error: {e}")
```

### Example 4: Sending a Request

```python
# Create an instance of the OpenAIChatClient
client = OpenAIChatClient(server_ip="localhost")

try:
 # Send a request to the OpenAI chat client
 client._send_request(data={"message": "Hello, OpenAI!"})
except Exception as e:
 print(f"Error: {e}")
```

Note: The above examples are simple and demonstrate the usage of each method. In a real-world scenario, you would likely want to handle errors and exceptions more robustly, and add additional logic to handle different scenarios.