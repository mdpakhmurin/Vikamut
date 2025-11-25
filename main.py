import os
import importlib
from datetime import datetime

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import time

import config
import filters

vk_session = vk_api.VkApi(token=config.vk_token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, config.vk_bot_group_id)

FILTERS_PATH = os.path.join(os.path.dirname(__file__), "filters.py")
last_modified = os.path.getmtime(FILTERS_PATH)

print(datetime.now(), "\t", "Bot started.")


def reload_filters_if_needed():
    global last_modified, filters
    try:
        current_mtime = os.path.getmtime(FILTERS_PATH)
        if current_mtime != last_modified:
            importlib.reload(filters)
            last_modified = current_mtime
            print(datetime.now(), "\t", "filters.py reloaded")
    except Exception as e:
        print(datetime.now(), "\t", "error loading filters.py", e)


while True:
    try:
        for event in longpoll.listen():
            try:
                reload_filters_if_needed()
            except:
                print(datetime.now(), "\t", "error loading filters.py")

            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.message

                try:
                    is_conversation = msg.conversation_message_id
                    if not is_conversation:
                        continue

                    if (config.peer_ids 
                        and len(config.peer_ids) != 0 
                        and msg.peer_id not in config.peer_ids):
                        continue

                    if filters.is_delete(msg):
                        vk.messages.delete(
                            peer_id=msg.peer_id,
                            cmids=[msg.conversation_message_id],
                            delete_for_all=1
                        )
                        print(
                            datetime.now(), 
                            "\t",
                            f"Message deleted (from: https://vk.com/id{msg.from_id}, peer_id:{msg.peer_id}): {msg.text}"
                        )
                except Exception as e:
                    print(datetime.now(), "\t", "error filtering message:", e)

    except Exception as e:
        print(datetime.now(), "\t", "Unexpected error:", e)
        time.sleep(30)
        continue
