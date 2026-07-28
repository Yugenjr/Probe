import requests, json

print("1. Creating Workspace")
ws = requests.post('http://localhost:8005/api/v1/workspaces', json={'title': 'Test', 'initial_blocks': []}).json()
print('Workspace:', ws)

print("\n2. Sending Chat Request")
import sseclient
response = requests.post(f"http://localhost:8005/api/v1/workspaces/{ws['id']}/chat", json={'message': 'We have a huge database failure.'}, stream=True)
client = sseclient.SSEClient(response)
for event in client.events():
    print(event.data)
