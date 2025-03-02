"""
web app and socket are here
"""

import asyncio
import logging
import json
from typing import Any

from quart import Quart
from quart import websocket

from services import get_or_create_user
from services import find_match
from services import handle_answer
from services import finish_game



app = Quart(__name__)

active_connections = {}  # {user_id: websocket}
pending_users = []



@app.websocket('/ws')
async def ws():
    # this is the web socket holding the connection
    try:
        user_id = await websocket.receive_json() # first message is BaleID
        _ = get_or_create_user(user_id) # user (we don't actually need it)

        active_connections[user_id] = websocket
        pending_users.append(user_id)

        # match pending users
        if len(pending_users) >= 2:
            player1 = pending_users.pop(0)
            player2 = pending_users.pop(0)

            # we won't have more then one pending users
            # 'cus if we had they would be matched
            game = find_match(player1)
            find_match(player2) # second user gets into the same match

            questions = [q.id for q in game.questions]

            await send_json(player1, {"type": "start", "game_id": game.id, "questions": questions})
            await send_json(player2, {"type": "start", "game_id": game.id, "questions": questions})

        while True:
            message = await websocket.receive_json()
            await handle_message(user_id, message)

    except Exception as e:
        logging.error(f"websocket got an exception: {e}")

    finally:
        active_connections.pop(user_id, None)



async def handle_message(user_id: str, message: dict[str, Any]) -> None:
    # handle recived messages from users
    msg_type = message.get("type")

    if msg_type == "answer":
        game_id = message.get("game_id")
        question_id = message.get("question_id")
        selected_option = message.get("selected_option")

        result = handle_answer(user_id, game_id, question_id, selected_option)

        if result:
            await send_json(user_id, {"type": "answer_result", "correct": result["correct"], "score": result["score"]})

    elif msg_type == "finish":
        game_id = message.get("game_id")
        results = finish_game(game_id)

        if results:
            for player_id, score in results.items():
                await send_json(player_id, {"type": "game_over", "score": score})



async def send_json(user_id: str, data: dict[str, Any]) -> None:
    # send a json file to the user
    if user_id in active_connections:
        await active_connections[user_id].send(json.dumps(data))



if __name__ == "__main__":
    app.run(port=5000)
