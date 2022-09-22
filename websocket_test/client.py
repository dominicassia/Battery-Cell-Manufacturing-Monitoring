import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8765") as websocket:
        message = 'Hello world!'
        await websocket.send(message)
        print(f'Sent: {message}')
        message = await websocket.recv()
        print(f'Received: {message}')
asyncio.run(hello())