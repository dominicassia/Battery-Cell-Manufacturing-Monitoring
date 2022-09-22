import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f'Received: {message}')
        await websocket.send(message)
        print(f'Sent: {message}')

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())