import os
import threading
import time
import traceback
from typing import Callable
from aiohttp import ClientError
import oracledb
from requests import HTTPError, RequestException

from datasource.ib_connector import IBConnector

from module.discord_chatbot_client import DiscordChatBotClient

from model.discord.discord_message import DiscordMessage

from utils.logger import Logger

from constant.discord.discord_channel import DiscordChannel

logger = Logger()

MAX_RETRY_CONNECTION_TIMES = 5
CONNECTION_FAIL_RETRY_INTERVAL = 10
SCANNER_FATAL_ERROR_REFRESH_INTERVAL = 5

STACKTRACE_CHUNK_SIZE = 2000

reauthentication_lock = threading.Lock()

class ScannerThreadWrapper(threading.Thread):
    def __init__(self, scan: Callable, 
                 name: str,
                 ib_connector: IBConnector,
                 discord_client: DiscordChatBotClient):
        self.exc = None
        self.__scan = scan
        self.__ib_connector = ib_connector
        self.__discord_client = discord_client
        super().__init__(name=name)
        
    def __reauthenticate(self):
        retry_times = 0

        with reauthentication_lock:
            while True:
                try:
                    if retry_times < MAX_RETRY_CONNECTION_TIMES:
                        logger.log_debug_msg('send reauthenticate requests', with_std_out=True)
                        self.__ib_connector.reauthenticate()
                    else:
                        raise RequestException("Reauthentication failed")
                except Exception as reauthenticate_exception:
                    if retry_times < MAX_RETRY_CONNECTION_TIMES:
                        self.__discord_client.send_message_by_list_with_response([DiscordMessage(content=f'Failed to re-authenticate session, retry after {CONNECTION_FAIL_RETRY_INTERVAL} seconds')], channel_type=DiscordChannel.TEXT_TO_SPEECH, with_text_to_speech=True)
                        logger.log_error_msg(f'Session re-authentication error, {reauthenticate_exception}', with_std_out=True)
                        retry_times += 1
                        time.sleep(CONNECTION_FAIL_RETRY_INTERVAL)
                        continue
                    else:
                        self.__discord_client.send_message(DiscordMessage(content=f'Maximum re-authentication attemps exceed. Please restart application'), channel_type=DiscordChannel.TEXT_TO_SPEECH, with_text_to_speech=True)
                        time.sleep(30)
                        os._exit(1)
                
                self.__discord_client.send_message_by_list_with_response([DiscordMessage(content='Reauthentication succeed')], channel_type=DiscordChannel.TEXT_TO_SPEECH, with_text_to_speech=True)
                logger.log_debug_msg('Reauthentication succeed', with_std_out=True)
                break    
            
    def run(self) -> None:  
        while True:
            try:
                self.__scan(self.__ib_connector, self.__discord_client)
            except (RequestException, ClientError, HTTPError) as connection_exception:
                self.__discord_client.send_message(DiscordMessage(content='Client Portal API connection failed, re-authenticating session'), channel_type=DiscordChannel.TEXT_TO_SPEECH, with_text_to_speech=True)
                logger.log_error_msg(f'Client Portal API connection error in stock screener, {connection_exception}', with_std_out=True)
                self.__reauthenticate()
            except oracledb.Error as oracle_connection_exception:
                self.__discord_client.send_message(DiscordMessage(content='Database connection error'), channel_type=DiscordChannel.CHATBOT_ERROR_LOG, with_text_to_speech=True)
                logger.log_error_msg(f'Oracle connection error, {oracle_connection_exception}', with_std_out=True)
            except Exception as exception:
                self.__discord_client.send_message(DiscordMessage(content='Fatal error'), channel_type=DiscordChannel.TEXT_TO_SPEECH, with_text_to_speech=True)   
                stacktrace = traceback.format_exc()
                
                if len(stacktrace) > STACKTRACE_CHUNK_SIZE:
                    stacktrace_chunk_list = stacktrace.split('\n')
                    send_chunk_list = []

                    counter = 0
                    total_no_of_char = 0
                    concat_chunk_str = ''
                    while counter < len(stacktrace_chunk_list):
                        line_txt = stacktrace_chunk_list[counter]
                        line_txt_length = len(line_txt)
                        total_no_of_char += line_txt_length

                        if total_no_of_char <= STACKTRACE_CHUNK_SIZE:
                            concat_chunk_str += line_txt
                            counter += 1
                            
                            if counter == len(stacktrace_chunk_list) - 1:
                                send_chunk_list.append(concat_chunk_str)
                        else:
                            send_chunk_list.append(concat_chunk_str)
                            total_no_of_char = 0
                            concat_chunk_str = ''
                            
                    for send_chunk in send_chunk_list:
                        self.__discord_client.send_message(DiscordMessage(content=send_chunk), channel_type=DiscordChannel.CHATBOT_ERROR_LOG)    
                else:
                    self.__discord_client.send_message(DiscordMessage(content=stacktrace), channel_type=DiscordChannel.CHATBOT_ERROR_LOG)
                    
                logger.log_error_msg(f'Scanner fatal error, {exception}', with_std_out=True)
                logger.log_error_msg(f'{traceback.format_exc()}')
                logger.log_debug_msg(f'Retry scanning due to fatal error after: {SCANNER_FATAL_ERROR_REFRESH_INTERVAL} seconds', with_std_out=True)
                time.sleep(SCANNER_FATAL_ERROR_REFRESH_INTERVAL)
                