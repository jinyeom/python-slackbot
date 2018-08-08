import os
import time
from datetime import datetime
import logging
import re
from enum import Enum

import fire
from slackclient import SlackClient


class BMO(object):
    def __init__(self, token_env_var="BMO_OAUTH_TOKEN", rtm_read_delay=1):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.INFO)

        self._magic = "^<@(|[WU].+?)>(.*)"
        self._rtm_read_delay = rtm_read_delay

        self._slack_client = SlackClient(self._get_oauth_access_token(token_env_var))
        if self._slack_client.rtm_connect(with_team_state=False):
            self._logger.info(f"[{datetime.now()}] BMO connected and running!")
            self._user_id = self._slack_client.api_call("auth.test")["user_id"]

    def _get_oauth_access_token(self, token_env_var):
        token = os.environ.get(token_env_var)
        if token is None:
            raise ValueError(f"No environment variable named {token_env_var}")
        return token

    def parse_direct_mention(self, message):
        matches = re.search(self._magic, message)
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def listen(self, slack_events):
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self._user_id:
                    now = datetime.now()
                    sender = event["user"]
                    self._logger.info(f"[{now}] {sender} said \"{message}\"")
                    return message, event["channel"]
        return None, None

    def respond(self, message, channel):
        if message is not None and channel is not None:
            # TODO: get a real response
            response = "What?"
            self._slack_client.api_call("chat.postMessage", channel=channel, text=response)

    def run(self):
        while True:
            # listen and respond
            self.respond(*self.listen(self._slack_client.rtm_read()))
            time.sleep(self._rtm_read_delay)


if __name__ == "__main__":
    fire.Fire(BMO)

