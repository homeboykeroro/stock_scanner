import datetime
import math
import time
import pandas as pd
import requests

from module.discord_chatbot_client import DiscordChatBotClient

from datasource.ib_connector import IBConnector

from pattern.initial_pop import InitialPop
from pattern.initial_dip import InitialDip
from pattern.previous_days_top_gainer_support import PreviousDayTopGainerSupport
from pattern.previous_days_top_gainer_continuation import PreviousDayTopGainerContinuation
from pattern.yesterday_bullish_daily_candle import YesterdayBullishDailyCandle
from pattern.intra_day_breakout import IntraDayBreakout

from model.discord.discord_message import DiscordMessage
from module.scanner_thread_wrapper import ScannerThreadWrapper

from utils.previous_day_top_gainer_util import get_previous_day_top_gainer_list
from utils.filter_util import get_ib_scanner_filter
from utils.datetime_util import PRE_MARKET_START_DATETIME, get_current_us_datetime, get_us_business_day
from utils.dataframe_util import append_customised_indicator
from utils.config_util import get_config
from utils.logger import Logger

from constant.scanner.scanner_target import ScannerTarget
from constant.candle.bar_size import BarSize
from constant.discord.discord_channel import DiscordChannel

idx = pd.IndexSlice
logger = Logger()

MAX_RETRY_CONNECTION_TIMES = 5
CONNECTION_FAIL_RETRY_INTERVAL = 10

# Day Trade
MAX_MARKET_CAP_FOR_DAY_TRADE_SCANNER = 1e6 * 500
MIN_PRICE_FOR_DAY_TRADE_SCANNER = 0.3
MAX_NO_OF_DAY_TRADE_SCANNER_RESULT = 15
IB_TOP_GAINER_FILTER = get_ib_scanner_filter(ScannerTarget.TOP_GAINER,
                                       min_price = MIN_PRICE_FOR_DAY_TRADE_SCANNER, 
                                       percent_change_param = 10, 
                                       min_usd_volume = 20000, 
                                       max_market_cap = MAX_MARKET_CAP_FOR_DAY_TRADE_SCANNER, 
                                       additional_filter_list = [])
IB_TOP_LOSER_FILTER = get_ib_scanner_filter(ScannerTarget.TOP_LOSER,
                                      min_price = MIN_PRICE_FOR_DAY_TRADE_SCANNER, 
                                      percent_change_param = -10, 
                                      min_usd_volume = 20000, 
                                      max_market_cap = MAX_MARKET_CAP_FOR_DAY_TRADE_SCANNER, 
                                      additional_filter_list = [])

SHOW_TOP_GAINER_SCANNER_DISCORD_DEBUG_LOG = get_config('TOP_GAINER_SCANNER', 'SHOW_DISCORD_DEBUG_LOG')
SHOW_TOP_LOSER_SCANNER_DISCORD_DEBUG_LOG = get_config('TOP_LOSER_SCANNER', 'SHOW_DISCORD_DEBUG_LOG')

INITIAL_POP_DAILY_CANDLE_DAYS = get_config('INITIAL_POP_PARAM', 'DAILY_CANDLE_DAYS')
INITIAL_DIP_DAILY_CANDLE_DAYS = get_config('INITIAL_DIP_PARAM', 'DAILY_CANDLE_DAYS')

MIN_YESTERDAY_CLOSE_CHANGE_PCT = get_config('YESTERDAY_BULLISH_DAILY_CANDLE_PARAM', 'MIN_YESTERDAY_CLOSE_CHANGE_PCT')
YESTERDAY_BULLISH_DAILY_CANDLE_DAYS = get_config('YESTERDAY_BULLISH_DAILY_CANDLE_PARAM', 'DAILY_CANDLE_DAYS')

MIN_MULTI_DAYS_CLOSE_CHANGE_PCT = get_config('MULTI_DAYS_TOP_GAINER_SCAN_PARAM', 'MIN_MULTI_DAYS_CLOSE_CHANGE_PCT')
MULTI_DAYS_TOP_GAINER_DAILY_CANDLE_DAYS = get_config('MULTI_DAYS_TOP_GAINER_SCAN_PARAM', 'DAILY_CANDLE_DAYS')

#IB_CLOSEST_TO_HALT_FILTER = get_ib_scanner_filter(ScanCode)

class Scanner:
    def __init__(self, discord_client: DiscordChatBotClient) -> None:
        self.__discord_client = discord_client
        self.__ib_connector = IBConnector()
        
        self.__daily_canlde_df = pd.DataFrame()
        self.__yesterday_top_gainier_minute_candle_df_dict = {
            BarSize.ONE_MINUTE: pd.DataFrame()
        }
        
    @property
    def ib_connector(self):
        return self.__ib_connector
    
    @ib_connector.setter
    def ib_connector(self, ib_connector):
        self.__ib_connector = ib_connector
    
    def send_ib_preflight_request(self):
        try:
            self.__ib_connector.receive_brokerage_account()
        except requests.exceptions.HTTPError as preflight_request_exception:
            #logger.log_error_msg(f'Client Portal API preflight requests error, {preflight_request_exception}', with_std_out=True)
            raise preflight_request_exception
        
    def check_auth_status(self):
        try:
            self.__ib_connector.check_auth_status()
        except requests.exceptions.HTTPError as check_auth_exception:
            raise check_auth_exception
    
    def scan_multi_days_top_gainer(self):
        thread = ScannerThreadWrapper(scan=self.__analyse_multi_days_top_gainer,
                                      name='multi_day_top_gainer_scan',
                                      ib_connector=self.__ib_connector,
                                      discord_client=self.__discord_client)
        thread.start()
        #thread.join()
        
    def scan_yesterday_top_gainer(self):
        thread = ScannerThreadWrapper(scan=self.__analyse_yesterday_top_gainer, 
                                      name='yesterday_top_gainer_scan',
                                      ib_connector=self.__ib_connector,
                                      discord_client=self.__discord_client)
        thread.start()
        #thread.join()
    
    def scan_intra_day_top_gainer(self):
        thread = ScannerThreadWrapper(scan=self.__analyse_intra_day_top_gainer, 
                                      name='intra_day_top_gainer_scan',
                                      ib_connector=self.__ib_connector,
                                      discord_client=self.__discord_client)
        thread.start()
        #thread.join()
    
    def scan_intra_day_top_loser(self):
        thread = ScannerThreadWrapper(scan=self.__analyse_intra_day_top_loser, 
                                      name='intra_day_top_loser_scan',
                                      ib_connector=self.__ib_connector,
                                      discord_client=self.__discord_client)
        thread.start()
        #thread.join()
    
    def __analyse_multi_days_top_gainer(self, ib_connector: IBConnector,
                                             discord_client: DiscordChatBotClient):
        logger.log_debug_msg('multi day top gainer scan starts')
        
        multi_days_top_gainer_contract_list = self.__get_previous_day_top_gainers_contracts(ib_connector=ib_connector,
                                                                                           min_pct_change=MIN_MULTI_DAYS_CLOSE_CHANGE_PCT,
                                                                                           offset=-MULTI_DAYS_TOP_GAINER_DAILY_CANDLE_DAYS,
                                                                                           retrieval_end_datetime=get_us_business_day()) 
        
        if not multi_days_top_gainer_contract_list:
            return

        request_candle_contract_list = [dict(symbol=contract.symbol, con_id=contract.con_id) for contract in multi_days_top_gainer_contract_list]
        multi_days_top_gainers_df = self.__get_daily_candle(ib_connector=ib_connector,
                                                              contract_list=request_candle_contract_list, 
                                                              offset_day=MULTI_DAYS_TOP_GAINER_DAILY_CANDLE_DAYS,
                                                              outside_rth=False)
        
        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3):
            logger.log_debug_msg('__analyse_multi_days_top_gainer daily df:')
            logger.log_debug_msg(multi_days_top_gainers_df)

        intra_day_one_minute_candle_df = self.__retrieve_intra_day_minute_candle(ib_connector=ib_connector,
                                                                                 contract_list=request_candle_contract_list, 
                                                                                 bar_size=BarSize.ONE_MINUTE)
    
        previous_day_top_gainer_support_analyser = PreviousDayTopGainerSupport(daily_df=multi_days_top_gainers_df,
                                                                               minute_df=intra_day_one_minute_candle_df,
                                                                               ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(), 
                                                                               discord_client=discord_client)
        previous_day_top_gainer_support_analyser.analyse()
        
        previous_day_top_gainer_continuation_analyser = PreviousDayTopGainerContinuation(daily_df=multi_days_top_gainers_df,
                                                                                         minute_df=intra_day_one_minute_candle_df,
                                                                                         ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(), 
                                                                                         discord_client=discord_client)
        previous_day_top_gainer_continuation_analyser.analyse()
        logger.log_debug_msg('Multi-day top gainer scan completed')
        
    def __analyse_yesterday_top_gainer(self, ib_connector: IBConnector, 
                                             discord_client: DiscordChatBotClient):
        logger.log_debug_msg('yesterday top gainer scan starts')

        us_current_datetime = get_current_us_datetime()
        day_offset = 0 if us_current_datetime.time() > datetime.time(16, 0, 0) else -1

        yesterday_top_gainer_retrieval_datetime = get_us_business_day(offset_day=day_offset, 
                                                                      us_date=us_current_datetime)
        yesterday_top_gainer_contract_list = self.__get_previous_day_top_gainers_contracts(ib_connector=ib_connector,
                                                                                           min_pct_change=MIN_YESTERDAY_CLOSE_CHANGE_PCT,
                                                                                           offset=day_offset) 

        if not yesterday_top_gainer_contract_list:
            return

        request_candle_contract_list = [dict(symbol=contract.symbol, con_id=contract.con_id) for contract in yesterday_top_gainer_contract_list]
        previous_day_top_gainers_df = self.__get_daily_candle(ib_connector=ib_connector,
                                                              contract_list=request_candle_contract_list, 
                                                              offset_day=YESTERDAY_BULLISH_DAILY_CANDLE_DAYS,
                                                              outside_rth=False,
                                                              candle_retrieval_end_datetime=yesterday_top_gainer_retrieval_datetime)
        
        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3):
            logger.log_debug_msg('__analyse_yesterday_top_gainer daily df')
            logger.log_debug_msg(previous_day_top_gainers_df)

        yesterday_bullish_daily_candle_analyser = YesterdayBullishDailyCandle(hit_scanner_date=yesterday_top_gainer_retrieval_datetime.date(),
                                                                              yesterday_top_gainer_contract_list=yesterday_top_gainer_contract_list,
                                                                              daily_df=previous_day_top_gainers_df,
                                                                              ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(), 
                                                                              discord_client=discord_client)
        yesterday_bullish_daily_candle_analyser.analyse()
        
        # intra_day_one_minute_candle_df = self.__retrieve_intra_day_minute_candle(ib_connector=ib_connector,
        #                                                                          contract_list=yesterday_top_gainer_contract_list, 
        #                                                                          bar_size=BarSize.ONE_MINUTE)
        # yesterday_one_minute_candle_df = self.__retrieve_yesterday_minute_candle(ib_connector=ib_connector,
        #                                                                          contract_list=yesterday_top_gainer_contract_list, 
        #                                                                          bar_size=BarSize.ONE_MINUTE)
        # concated_one_minute_candle_df = pd.concat([yesterday_one_minute_candle_df,
        #                                            intra_day_one_minute_candle_df], axis=0)

        # with pd.option_context('display.max_rows', None,
        #            'display.max_columns', None,
        #            'display.precision', 3):
        #     logger.log_debug_msg(f'yesterday top gainer\'s intra_day_one_minute_candle_df: {intra_day_one_minute_candle_df}', with_log_file=True, with_std_out=False)
        #     logger.log_debug_msg(f'yesterday top gainer\'s yesterday_one_minute_candle_df: {yesterday_one_minute_candle_df}', with_log_file=True, with_std_out=False)
        #     logger.log_debug_msg(f'yesterday top gainer\'s concated_one_minute_candle_df: {concated_one_minute_candle_df}', with_log_file=True, with_std_out=False)

        logger.log_debug_msg('Yesterday top gainer scan completed')
        
    def __analyse_intra_day_top_gainer(self, ib_connector: IBConnector,
                                             discord_client: DiscordChatBotClient) -> None:
        logger.log_debug_msg('Intra day top gainer scan starts')

        contract_list = self.__ib_connector.get_screener_results(MAX_NO_OF_DAY_TRADE_SCANNER_RESULT, IB_TOP_GAINER_FILTER)
        
        logger.log_debug_msg(f'Fetch top gainer snapshot')
        ib_connector.update_contract_info(contract_list)
        ticker_to_contract_dict = ib_connector.get_ticker_to_contract_dict()
        snapshot_list = [dict(symbol=contract.symbol, company_name=contract.company_name) for _, contract in ticker_to_contract_dict.items()]
        logger.log_debug_msg(f'Top gainer snapshot list: {snapshot_list}, size: {len(snapshot_list)}')
        logger.log_debug_msg(f'Initial pop scanner contract retrieval completed')
        
        logger.log_debug_msg('Retrieve top gainer one minute candle')
        one_minute_candle_df = self.__retrieve_intra_day_minute_candle(ib_connector=ib_connector,
                                                                       contract_list=contract_list, 
                                                                       bar_size=BarSize.ONE_MINUTE)
        logger.log_debug_msg(f'Top gainer one minute candle ticker: {one_minute_candle_df.columns.get_level_values(0).unique().tolist()}')
        
        logger.log_debug_msg('Retrieve top gainer daily candle')
        daily_df = self.__get_daily_candle(ib_connector=ib_connector,
                                           contract_list=contract_list, 
                                           offset_day=INITIAL_POP_DAILY_CANDLE_DAYS, 
                                           outside_rth=False)
        logger.log_debug_msg(f'Top gainer daily_df candle ticker: {daily_df.columns.get_level_values(0).unique().tolist()}')

        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3):
            logger.log_debug_msg('__analyse_intra_day_top_gainer daily df:')
            logger.log_debug_msg(daily_df)

        logger.log_debug_msg(f'Top gainer scanner result: {[contract["symbol"] for contract in contract_list]}')
        
        if SHOW_TOP_GAINER_SCANNER_DISCORD_DEBUG_LOG:
            send_msg_start_time = time.time()
            discord_client.send_message(DiscordMessage(content=f'{[contract["symbol"] for contract in contract_list]}'), DiscordChannel.TOP_GAINER_SCANNER_LIST)
            logger.log_debug_msg(f'Send top gainer scanner result time: {time.time() - send_msg_start_time}')

        initial_pop_analyser = InitialPop(bar_size=BarSize.ONE_MINUTE,
                                          historical_data_df=one_minute_candle_df, 
                                          daily_df=daily_df, 
                                          ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(), 
                                          discord_client=discord_client)
        initial_pop_analyser.analyse()
        
        intra_day_breakout_analyser = IntraDayBreakout(bar_size=BarSize.ONE_MINUTE,
                                                       historical_data_df=one_minute_candle_df,
                                                       daily_df=daily_df,
                                                       ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(),
                                                       discord_client=discord_client)
        intra_day_breakout_analyser.analyse()
        
    
    def __analyse_intra_day_top_loser(self, ib_connector: IBConnector,
                                            discord_client: DiscordChatBotClient) -> None:
        logger.log_debug_msg('Intra day top loser scan starts')
        
        contract_list = ib_connector.get_screener_results(MAX_NO_OF_DAY_TRADE_SCANNER_RESULT, IB_TOP_LOSER_FILTER)
        
        logger.log_debug_msg(f'Fetch top loser snapshot')
        ib_connector.update_contract_info(contract_list)
        ticker_to_contract_dict = ib_connector.get_ticker_to_contract_dict()
        snapshot_list = [dict(symbol=contract.symbol, company_name=contract.company_name) for _, contract in ticker_to_contract_dict.items()]
        logger.log_debug_msg(f'Top loser snapshot list: {snapshot_list}, size: {len(snapshot_list)}')
        logger.log_debug_msg(f'Initial dip scanner retrieval completed')
        
        logger.log_debug_msg('Retrieve top loser one minute candle')
        one_minute_candle_df = self.__retrieve_intra_day_minute_candle(ib_connector=ib_connector,
                                                                       contract_list=contract_list, 
                                                                       bar_size=BarSize.ONE_MINUTE)
        logger.log_debug_msg(f'Top loser one minute candle ticker: {one_minute_candle_df.columns.get_level_values(0).unique().tolist()}')
        
        logger.log_debug_msg('Retrieve top loser daily candle')
        daily_df = self.__get_daily_candle(ib_connector=ib_connector,
                                           contract_list=contract_list, 
                                           offset_day=INITIAL_DIP_DAILY_CANDLE_DAYS, 
                                           outside_rth=False)
        logger.log_debug_msg(f'Top loser daily candle ticker: {daily_df.columns.get_level_values(0).unique().tolist()}')

        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3):
            logger.log_debug_msg('__analyse_intra_day_top_loser daily df:')
            logger.log_debug_msg(daily_df)

        logger.log_debug_msg(f'Top loser scanner result: {[contract["symbol"] for contract in contract_list]}')
        
        if SHOW_TOP_LOSER_SCANNER_DISCORD_DEBUG_LOG:
            send_msg_start_time = time.time()
            discord_client.send_message(DiscordMessage(content=f'{[contract["symbol"] for contract in contract_list]}'), DiscordChannel.TOP_LOSER_SCANNER_LIST)
            logger.log_debug_msg(f'Send top loser scanner result time: {time.time() - send_msg_start_time}')
        
        initial_dip_analyser = InitialDip(bar_size=BarSize.ONE_MINUTE,
                                          historical_data_df=one_minute_candle_df, 
                                          daily_df=daily_df, 
                                          ticker_to_contract_info_dict=ib_connector.get_ticker_to_contract_dict(), 
                                          discord_client=discord_client)
        initial_dip_analyser.analyse()
        
        logger.log_debug_msg('Intra-day top loser scan completed')
    
    def scan_closest_to_halt(self):
        pass
    
    def scan_halted(self):
        pass

    def __retrieve_intra_day_minute_candle(self, ib_connector: IBConnector,
                                                 contract_list: list, 
                                                 bar_size: BarSize) -> pd.DataFrame:
        us_current_datetime = get_current_us_datetime().replace(microsecond=0, second=0)
        historical_data_interval_in_minute = (us_current_datetime - PRE_MARKET_START_DATETIME).total_seconds() / 60
        logger.log_debug_msg(f'Historical candle data retrieval period: {historical_data_interval_in_minute} minutes')

        if historical_data_interval_in_minute < 1:
            logger.log_debug_msg('Historical candle data retrieval retrieval period is less than 1 minute', with_std_out=True)
            return None
        else:
            candle_df = ib_connector.get_historical_candle_df(contract_list=contract_list, 
                                                              period=f'{math.floor(historical_data_interval_in_minute)}min', 
                                                              bar_size=bar_size, 
                                                              outside_rth='true')
            
            if candle_df is not None and not candle_df.empty:
                return append_customised_indicator(candle_df)
            else:
                return pd.DataFrame()
    
    def __retrieve_yesterday_minute_candle(self, ib_connector: IBConnector,
                                                 contract_list: list, 
                                                 bar_size: BarSize, 
                                                 outside_rth: bool = True):
        candle_request_contract_list = []
        contract_ticker_list = [contract['symbol'] for contract in contract_list]
        minute_candle_df = self.__yesterday_top_gainier_minute_candle_df_dict[bar_size]
        yesterday_top_gainer_ticker_list = list(minute_candle_df.columns.get_level_values(0).unique())
        
        for contract in contract_list:
            if contract['symbol'] not in yesterday_top_gainer_ticker_list:
                candle_request_contract_list.append(contract)
        
        select_contract_ticker_list = []

        if candle_request_contract_list:
            candle_retrieval_end_datetime = get_us_business_day(offset_day=-1)
            
            if outside_rth:
                outside_rth_str = 'true'
                candle_retrieval_end_datetime = candle_retrieval_end_datetime.replace(hour=20, minute=0, second=0, microsecond=0)
            else:
                outside_rth_str = 'false'
                candle_retrieval_end_datetime = candle_retrieval_end_datetime.replace(hour=16, minute=0, second=0, microsecond=0)

            candle_df = ib_connector.get_historical_candle_df(contract_list=candle_request_contract_list, 
                                                                     period='960min', 
                                                                     bar_size=bar_size, 
                                                                     outside_rth=outside_rth_str, 
                                                                     candle_retrieval_end_datetime=candle_retrieval_end_datetime)
            
            if candle_df is not None and not candle_df.empty:
                complete_df = append_customised_indicator(candle_df)
            
                self.__yesterday_top_gainier_minute_candle_df_dict[bar_size] = pd.concat([self.__yesterday_top_gainier_minute_candle_df_dict[bar_size],
                                                                                          complete_df], axis=1)
        
        result_df_ticker_list = self.__yesterday_top_gainier_minute_candle_df_dict[bar_size].columns.get_level_values(0).unique()
        
        for ticker in contract_ticker_list:
            if ticker in result_df_ticker_list:
                select_contract_ticker_list.append(ticker)
            else:
                logger.log_debug_msg(f'Exclude ticker {ticker} from yesterday_top_gainer_minute_candle_df[{bar_size}], no historical data found', with_std_out=True)
        
        return self.__yesterday_top_gainier_minute_candle_df_dict[bar_size].loc[:, idx[select_contract_ticker_list, :]]
    
    def __get_daily_candle(self, ib_connector: IBConnector, 
                                 contract_list: list, 
                                 offset_day: int, 
                                 outside_rth: bool = False, 
                                 candle_retrieval_end_datetime: datetime.datetime = None) -> pd.DataFrame:
        candle_request_contract_list = []
        contract_ticker_list = [contract['symbol'] for contract in contract_list]
        daily_candle_df_ticker_list = list(self.__daily_canlde_df.columns.get_level_values(0).unique())

        for contract in contract_list:
            if contract['symbol'] not in daily_candle_df_ticker_list:
                candle_request_contract_list.append(contract)

        if candle_request_contract_list:    
            if outside_rth:
                outside_rth_str = 'true' 
            else:
                outside_rth_str = 'false'
            
            candle_df = ib_connector.get_historical_candle_df(contract_list=candle_request_contract_list, 
                                                              period=f'{offset_day}d', 
                                                              bar_size=BarSize.ONE_DAY, 
                                                              outside_rth=outside_rth_str, 
                                                              candle_retrieval_end_datetime=candle_retrieval_end_datetime)
            if candle_df is not None and not candle_df.empty:
                complete_df = append_customised_indicator(candle_df)

                self.__daily_canlde_df = pd.concat([self.__daily_canlde_df,
                                                    complete_df], axis=1)

        result_df_ticker_list = self.__daily_canlde_df.columns.get_level_values(0).unique()
        select_contract_ticker_list = []
        
        for ticker in contract_ticker_list:
            if ticker in result_df_ticker_list:
                select_contract_ticker_list.append(ticker)
            else:
                logger.log_debug_msg(f'Exclude ticker {ticker} from daily_df, no historical data found', with_std_out=True)

        start_date_range = get_us_business_day(-offset_day, candle_retrieval_end_datetime).date()
        return self.__daily_canlde_df.loc[start_date_range:, idx[select_contract_ticker_list, :]]

    def __get_previous_day_top_gainers_contracts(self, ib_connector: IBConnector,
                                                       min_pct_change,
                                                       offset: int = None, 
                                                       retrieval_end_datetime: datetime = None):
        retrieval_start_datetime = get_us_business_day(offset)
        
        if not retrieval_end_datetime:
            retrieval_end_datetime = retrieval_start_datetime
        
        previous_day_top_gainer_list = get_previous_day_top_gainer_list(pct_change=min_pct_change, 
                                                                        start_datetime=retrieval_start_datetime, 
                                                                        end_datetime=retrieval_end_datetime)
        
        if not previous_day_top_gainer_list:
            return []
        
        ticker_list = list(set([top_gainer[0] for top_gainer in previous_day_top_gainer_list]))

        previous_day_top_gainer_contract_list = ib_connector.get_security_by_tickers(ticker_list)
        ib_connector.update_contract_info(previous_day_top_gainer_contract_list)
        ticker_to_contract_dict = ib_connector.get_ticker_to_contract_dict()
        
        contract_dict_list = []
        
        for ticker, contract in ticker_to_contract_dict.items():
            if ticker in ticker_list:
                contract_dict_list.append(contract)
        
        return contract_dict_list
    