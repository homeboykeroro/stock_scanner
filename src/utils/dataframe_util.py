import time
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

from utils.logger import Logger

from constant.indicator.runtime_indicator import RuntimeIndicator
from constant.indicator.indicator import Indicator
from constant.candle.candle_colour import CandleColour
from constant.indicator.customised_indicator import CustomisedIndicator

logger = Logger()
idx = pd.IndexSlice

def derive_idx_df(src_df: DataFrame, numeric_idx: bool = True) -> DataFrame:
    if numeric_idx:
        idx_np = src_df.reset_index(drop=True).reset_index().iloc[:, [0]].values
    else:
        idx_np = src_df.reset_index().iloc[:, [0]].values
    
    return pd.DataFrame(np.repeat(idx_np, len(src_df.columns), axis=1), 
                        columns=src_df.columns).rename(columns={src_df.columns.get_level_values(1).values[0]: RuntimeIndicator.INDEX.value})

def get_sorted_value_without_duplicate_df(src_df: DataFrame) -> DataFrame:
    sorted_np = np.sort(src_df.values, axis=0)
    _, indices = np.unique(sorted_np.flatten(), return_inverse=True)
    mask = np.ones(sorted_np.size, dtype=bool)
    mask[indices] = False
    mask = mask.reshape(sorted_np.shape)
    sorted_np[mask] = -1
    sorted_df = pd.DataFrame(np.sort(sorted_np, axis=0), 
                             columns=src_df.columns).replace(-1, np.nan)   
    
    return sorted_df

def get_idx_df_by_value_df(val_src_df: DataFrame, idx_src_df: DataFrame, numeric_idx: bool = True) -> DataFrame:
    result_df = val_src_df.copy()
    
    if numeric_idx:
        reference_df = idx_src_df.reset_index(drop=True)
    else:
        reference_df = idx_src_df
    
    for column in result_df.columns:
        result_df[column] = result_df[column].apply(lambda x: reference_df.index[reference_df[column] == x][0] if pd.notnull(x) else np.nan)
    
    return result_df

def append_customised_indicator(src_df: pd.DataFrame) -> pd.DataFrame:
    construct_dataframe_start_time = time.time()
    open_df = src_df.loc[:, idx[:, Indicator.OPEN.value]].rename(columns={Indicator.OPEN.value: RuntimeIndicator.COMPARE.value})
    close_df = src_df.loc[:, idx[:, Indicator.CLOSE.value]].rename(columns={Indicator.CLOSE.value: RuntimeIndicator.COMPARE.value})
    vol_df = src_df.loc[:, idx[:, Indicator.VOLUME.value]]

    close_pct_df = close_df.pct_change().mul(100).rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.CLOSE_CHANGE.value})
    
    flat_candle_df = (open_df == close_df).replace({True: CandleColour.GREY.value, False: np.nan})
    green_candle_df = (close_df > open_df).replace({True: CandleColour.GREEN.value, False: np.nan})
    red_candle_df = (close_df < open_df).replace({True: CandleColour.RED.value, False: np.nan})
    colour_df = ((flat_candle_df.fillna(green_candle_df))
                                .fillna(red_candle_df)
                                .rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.CANDLE_COLOUR.value}))

    vol_cumsum_df = vol_df.cumsum().rename(columns={Indicator.VOLUME.value: CustomisedIndicator.TOTAL_VOLUME.value})

    close_above_open_boolean_df = (close_df > open_df)
    close_above_open_upper_body_df = close_df.where(close_above_open_boolean_df.values)
    open_above_close_upper_body_df = open_df.where((~close_above_open_boolean_df).values)
    candle_upper_body_df = close_above_open_upper_body_df.fillna(open_above_close_upper_body_df)

    close_above_open_lower_body_df = open_df.where(close_above_open_boolean_df.values)
    open_above_close_lower_body_df = close_df.where((~close_above_open_boolean_df).values)
    candle_lower_body_df = close_above_open_lower_body_df.fillna(open_above_close_lower_body_df)

    shifted_upper_body_df = candle_upper_body_df.shift(periods=1)
    shifted_lower_body_df = candle_lower_body_df.shift(periods=1)
    gap_up_boolean_df = (candle_lower_body_df > shifted_upper_body_df)
    gap_down_boolean_df = (candle_upper_body_df < shifted_lower_body_df)
    no_gap_boolean_df = ((~gap_up_boolean_df) & (~gap_down_boolean_df))
    
    gap_up_pct_df = (((candle_lower_body_df.sub(shifted_upper_body_df.values))
                                           .div(shifted_upper_body_df.values))
                                           .mul(100)
                                           .where(gap_up_boolean_df.values)).rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.GAP_PCT_CHANGE.value})
    gap_down_pct_df = (((candle_upper_body_df.sub(shifted_lower_body_df.values))
                                             .div(candle_upper_body_df.values))
                                             .mul(100)
                                             .where(gap_down_boolean_df.values)).rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.GAP_PCT_CHANGE.value})
    gap_pct_df = ((gap_up_pct_df.fillna(gap_down_pct_df)
                                .where(~no_gap_boolean_df.values)))
        
    complete_df = pd.concat([src_df, 
                            close_pct_df,
                            gap_pct_df,
                            vol_cumsum_df,
                            colour_df,
                            candle_lower_body_df.rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.CANDLE_LOWER_BODY.value}),
                            candle_upper_body_df.rename(columns={RuntimeIndicator.COMPARE.value: CustomisedIndicator.CANDLE_UPPER_BODY.value})], axis=1)

    logger.log_debug_msg(f'Construct customised statistics dataframe time: {time.time() - construct_dataframe_start_time}')
    return complete_df
