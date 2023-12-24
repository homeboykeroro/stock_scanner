from enum import Enum

class DiscordChannel(str, Enum):
    DAY_TRADE_FLOOR = 'DAY_TRADE_FLOOR'
    SWING_TRADE_FLOOR = 'SWING_TRADE_FLOOR'
    TEXT_TO_SPEECH = 'TEXT_TO_SPEECH'
    CHATBOT_LOG = 'CHATBOT_LOG'