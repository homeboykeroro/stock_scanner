import math
import time
import pandas as pd
from pandas.core.frame import DataFrame

from pattern.pattern_analyser import PatternAnalyser

from model.discord.scanner_result_message import ScannerResultMessage

from constant.indicator.indicator import Indicator
from constant.indicator.customised_indicator import CustomisedIndicator
from constant.indicator.runtime_indicator import RuntimeIndicator
from constant.indicator.scatter_symbol import ScatterSymbol
from constant.indicator.scatter_colour import ScatterColour
from constant.candle.candle_colour import CandleColour
from constant.candle.bar_size import BarSize
from constant.discord.discord_channel import DiscordChannel

from utils.chart_util import get_candlestick_chart
from utils.dataframe_util import replace_daily_df_latest_day_with_minute, get_ticker_to_occurrence_idx_list
from utils.datetime_util import convert_into_human_readable_time, convert_into_read_out_time, get_current_us_datetime
from utils.logger import Logger
from utils.config_util import get_config

idx = pd.IndexSlice
logger = Logger()

PATTERN_NAME = 'INITIAL_DIP'

MAX_TOLERANCE_PERIOD_IN_MINUTE = get_config('INITIAL_DIP_PARAM', 'MAX_TOLERANCE_PERIOD_IN_MINUTE')
MAX_DIP_OCCURRENCE = get_config('INITIAL_DIP_PARAM', 'MAX_DIP_OCCURRENCE')
MAX_GAP_DOWN_PCT = get_config('INITIAL_DIP_PARAM', 'MAX_GAP_DOWN_PCT')
MAX_YESTERDAY_CLOSE_TO_LAST_PCT = get_config('INITIAL_DIP_PARAM', 'MAX_YESTERDAY_CLOSE_TO_LAST_PCT')
MINUTE_CANDLE_POSITIVE_OFFSET = get_config('INITIAL_DIP_PARAM', 'MINUTE_CANDLE_POSITIVE_OFFSET')
MINUTE_CANDLE_NEGATIVE_OFFSET = get_config('INITIAL_DIP_PARAM', 'MINUTE_CANDLE_NEGATIVE_OFFSET')

class InitialDip(PatternAnalyser):
        
    def __init__(self, bar_size: BarSize, historical_data_df: DataFrame, daily_df: DataFrame, ticker_to_contract_info_dict: dict, discord_client):
        ticker_list = list(historical_data_df.columns.get_level_values(0).unique())
        super().__init__(discord_client)
        self.__bar_size = bar_size
        self.__historical_data_df = historical_data_df
        
        daily_df_ticker_list = daily_df.columns.get_level_values(0).unique().tolist()
        select_daily_df_ticker_list = []
        for ticker in ticker_list:
            if ticker in daily_df_ticker_list:
                select_daily_df_ticker_list.append(ticker)
        
        self.__daily_df = daily_df.loc[:, idx[select_daily_df_ticker_list, :]]
        self.__ticker_to_contract_info_dict = ticker_to_contract_info_dict

    def analyse(self) -> None:
        message_list = []
        logger.log_debug_msg('Initial dip scan')
        start_time = time.time()
        
        yesterday_daily_candle_df = self.__daily_df.iloc[[-1]]
        candle_colour_df = self.__historical_data_df.loc[:, idx[:, CustomisedIndicator.CANDLE_COLOUR.value]]
        close_df = self.__historical_data_df.loc[:, idx[:, Indicator.CLOSE.value]]
        
        yesterday_close_df = yesterday_daily_candle_df.loc[:, idx[:, Indicator.CLOSE.value]]
        yesterday_close_to_last_pct_df = (close_df.sub(yesterday_close_df.values)
                                                  .div(yesterday_close_df.values)
                                                  .mul(100))

        yesterday_lower_body_df = yesterday_daily_candle_df.loc[:, idx[:, CustomisedIndicator.CANDLE_LOWER_BODY.value]]
        upper_body_df = self.__historical_data_df.loc[:, idx[:, CustomisedIndicator.CANDLE_UPPER_BODY.value]]
        gap_down_pct_df = (upper_body_df.sub(yesterday_lower_body_df.values)
                                        .div(yesterday_lower_body_df.values)
                                        .mul(100))
        
        self.__historical_data_df.loc[[self.__historical_data_df.index[0]], idx[:, CustomisedIndicator.CLOSE_CHANGE.value]] = yesterday_close_to_last_pct_df.iloc[[0]]
        self.__historical_data_df.loc[[self.__historical_data_df.index[0]], idx[:, CustomisedIndicator.GAP_PCT_CHANGE.value]] = gap_down_pct_df.iloc[[0]]
        
        max_gap_down_pct_df = (gap_down_pct_df <= MAX_GAP_DOWN_PCT).rename(columns={CustomisedIndicator.CANDLE_UPPER_BODY.value: RuntimeIndicator.COMPARE.value})
        max_yesterday_close_to_last_pct_boolean_df = (yesterday_close_to_last_pct_df <= MAX_YESTERDAY_CLOSE_TO_LAST_PCT).rename(columns={Indicator.CLOSE.value: RuntimeIndicator.COMPARE.value})
        red_candle_candle_df = (candle_colour_df == CandleColour.RED.value).rename(columns={CustomisedIndicator.CANDLE_COLOUR.value: RuntimeIndicator.COMPARE.value})
        
        dip_boolean_df = (max_gap_down_pct_df) & (max_yesterday_close_to_last_pct_boolean_df) & (red_candle_candle_df)

        loser_result_series = dip_boolean_df.any()   
        loser_ticker_list = loser_result_series.index[loser_result_series].get_level_values(0).tolist()
        
        ticker_to_occurrence_idx_list_dict = get_ticker_to_occurrence_idx_list(dip_boolean_df, MAX_DIP_OCCURRENCE)
        logger.log_debug_msg(f'Initial dip ticker to occurrence idx list: {ticker_to_occurrence_idx_list_dict}')
        logger.log_debug_msg(f'Initial dip analysis time: {time.time() - start_time} seconds')
    
        if len(loser_ticker_list) > 0:
            for ticker in loser_ticker_list:
                occurrence_idx_list = ticker_to_occurrence_idx_list_dict[ticker]

                for occurrence_idx in occurrence_idx_list:   
                    if not occurrence_idx:
                        continue
                    else:
                        us_current_datetime = get_current_us_datetime()
                        current_datetime_and_pop_up_time_diff = math.floor(((us_current_datetime.replace(tzinfo=None) - occurrence_idx).total_seconds()) / 60)
                        
                        if current_datetime_and_pop_up_time_diff > MAX_TOLERANCE_PERIOD_IN_MINUTE:
                            logger.log_debug_msg(f'Exclude {ticker} initial dip at {occurrence_idx}, analysis datetime: {us_current_datetime}, out of tolerance period')
                            continue
                    
                    dip_time = occurrence_idx
                    check_message_sent_start_time = time.time()
                    is_message_sent = self.check_if_pattern_analysis_message_sent(ticker=ticker, hit_scanner_datetime=dip_time.replace(second=0, microsecond=0), pattern=PATTERN_NAME, bar_size=self.__bar_size)
                    logger.log_debug_msg(f'Check {ticker} dip pattern message send time: {time.time() - check_message_sent_start_time} seconds')

                    if not is_message_sent:
                        with pd.option_context('display.max_rows', None,
                                               'display.max_columns', None,
                                            'display.precision', 3):
                            logger.log_debug_msg(f'{ticker} Dip Boolean Dataframe:')
                            logger.log_debug_msg(dip_boolean_df.loc[:, idx[[ticker], :]])
                            logger.log_debug_msg(f'{ticker} Initial Dip Full Dataframe:')
                            logger.log_debug_msg(self.__historical_data_df.loc[:, idx[[ticker], :]])
                        
                        contract_info = self.__ticker_to_contract_info_dict[ticker]
                        close = self.__historical_data_df.loc[dip_time, (ticker, Indicator.CLOSE.value)]
                        volume = self.__historical_data_df.loc[dip_time, (ticker, Indicator.VOLUME.value)]
                        total_volume = self.__historical_data_df.loc[dip_time, (ticker, CustomisedIndicator.TOTAL_VOLUME.value)]
                        yesterday_close = yesterday_close_df.loc[yesterday_close_df.index[-1], (ticker, Indicator.CLOSE.value)]
                        yesterday_close_to_last_pct = yesterday_close_to_last_pct_df.loc[dip_time, (ticker, Indicator.CLOSE.value)]

                        daily_df = replace_daily_df_latest_day_with_minute(daily_df=self.__daily_df.loc[:, idx[[ticker], :]], 
                                                                           minute_df=self.__historical_data_df.loc[[dip_time], idx[[ticker], :]])
                        
                        one_minute_chart_start_time = time.time()
                        logger.log_debug_msg(f'Generate {ticker} initial dip one minute chart')
                        minute_chart_dir = get_candlestick_chart(candle_data_df=self.__historical_data_df,
                                                                 ticker=ticker, pattern=PATTERN_NAME, bar_size=self.__bar_size,
                                                                 hit_scanner_datetime=dip_time,
                                                                 positive_offset=MINUTE_CANDLE_POSITIVE_OFFSET, negative_offset=MINUTE_CANDLE_NEGATIVE_OFFSET,
                                                                 scatter_symbol=ScatterSymbol.DIP, scatter_colour=ScatterColour.PURPLE)
                        logger.log_debug_msg(f'Generate {ticker} initial dip one minute chart finished time: {time.time() - one_minute_chart_start_time} seconds')
                        
                        daily_chart_start_time = time.time()
                        logger.log_debug_msg(f'Generate {ticker} initial pop daily chart')
                        daily_chart_dir = get_candlestick_chart(candle_data_df=daily_df,
                                                                ticker=ticker, pattern=PATTERN_NAME, bar_size=BarSize.ONE_DAY,
                                                                hit_scanner_datetime=daily_df.index[-1],
                                                                scatter_symbol=ScatterSymbol.DIP, scatter_colour=ScatterColour.PURPLE)
                        logger.log_debug_msg(f'Generate {ticker} initial pop daily chart finished time: {time.time() - daily_chart_start_time} seconds')
                        
                        hit_scanner_datetime_display = convert_into_human_readable_time(dip_time)
                        read_out_dip_time = convert_into_read_out_time(dip_time)
                        
                        message = ScannerResultMessage(title=f'{ticker} is dipping {round(yesterday_close_to_last_pct, 2)}% at {hit_scanner_datetime_display}',
                                                       readout_msg=f'{" ".join(ticker)} is dipping {round(yesterday_close_to_last_pct, 2)}% at {read_out_dip_time}',
                                                       close=close,
                                                       yesterday_close=yesterday_close,
                                                       volume=volume, total_volume=total_volume,
                                                       contract_info=contract_info,
                                                       minute_chart_dir=minute_chart_dir,
                                                       daily_chart_dir=daily_chart_dir, 
                                                       ticker=ticker,
                                                       hit_scanner_datetime=dip_time.replace(second=0, microsecond=0),
                                                       pattern=PATTERN_NAME,
                                                       bar_size=self.__bar_size.value)
                        message_list.append(message)

        if message_list:
            send_msg_start_time = time.time()
            self.send_notification(message_list, DiscordChannel.INITIAL_DIP)
            logger.log_debug_msg(f'{PATTERN_NAME} send message time: {time.time() - send_msg_start_time} seconds')
    