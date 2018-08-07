import os
import time
import logging
import re
from slackclient import SlackClient


SLACK_BOT_TOKEN = "SLACK_BOT_TOKEN"


RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# retrieve OAuth access token from environment variable
token = os.environ.get("SLACK_BOT_TOKEN")
if token is None:
    logger.error("OAuth access token not found")
    exit()

slack_client = SlackClient(token)
amo_id = None # assigned when server initializes


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == amo_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message):
    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    default_response = f"Not sure what you mean. Try {EXAMPLE_COMMAND}."
    response = None
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure... write some more code then I can do that :p"

    slack_client.api_call("chat.postMessage", channel=channel, text=response or default_response)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        logger.info("Amo connected and running...")
        amo_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        logger.error("Connection failed...")
