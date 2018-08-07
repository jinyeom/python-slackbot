import os
import time
import logging
import re
from enum import Enum

import fire
from slackclient import SlackClient


class BmoCommand(Enum):
    Hello = "hello"

class BmoResponse(Enum):
    Default = "Not sure what you mean..."
    Hello = "Hello!"
    

class Bmo(object):
    def __init__(self, token_env_var: str = "SLACK_BOT_TOKEN"):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.INFO)

        try:
            token = self._get_oauth_access_token(token_env_var)
        except ValueError:
            self._logger.error(f"Failed to initialize {self.__class__.__name__}")
        self._slack_client = SlackClient(token)
        self._user_id = self._slack_client.api_call("auth.test")["user_id"]



        

    def _get_oauth_access_token(self, token_env_var: str):
        token = os.environ.get(token_env_var)
        if token is None:
            raise ValueError(f"No environment variable named {token_env_var}")
        return token

    def run(self):
        pass


if __name__ == "__main__":
    fire.Fire(Bmo)

