# Quiz Bot
A quiz bot mini app (on bale messanger)

## Table of Contents
- [Setup](#setup)
  - [Configuration File](#configuration-file)
- [Testing Instructions](#testing-instructions)
- [License](#license)


## Setup
...

### Configuration File
an example of a `config.py` file
```python
DATABASE_URL = "sqlite+aiosqlite:///mydb.sqlite3"
```

## Testing Instructions
install dependencies using cmd
```
pip install websocket
```
run the following python script (while server is running)
```python
import asyncio
import websockets
import json

async def test_client(user_id):
    uri = "ws://localhost:5000/ws"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"user_id": user_id}))  # ارسال شناسه کاربر

        while True:
            message = await ws.recv()  # دریافت پیام از سرور
            print(f"[{user_id}] Received:", message)

            data = json.loads(message)

            if data["type"] == "start":
                game_id = data["game_id"]
                question_id = data["questions"][0]

                # ارسال یک پاسخ نمونه
                await ws.send(json.dumps({
                    "type": "answer",
                    "game_id": game_id,
                    "question_id": question_id,
                    "selected_option": "گزینه ۱"
                }))

            elif data["type"] == "answer_result":
                print(f"[{user_id}] Answer Result: {data}")

            elif data["type"] == "game_over":
                print(f"[{user_id}] Game Over! Score: {data['score']}")
                break  # تست تمام می‌شود

async def main():
    await asyncio.gather(test_client("user_1"), test_client("user_2"))

asyncio.run(main())
```
## License
...
