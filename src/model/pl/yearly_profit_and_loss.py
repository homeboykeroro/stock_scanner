import calendar
from datetime import datetime
import discord

from model.discord.discord_message import DiscordMessage

from constant.broker import Broker

class YearlyProfitAndLoss(DiscordMessage):
    def __init__(self, start_year_date: datetime = None,
                       end_year_date: datetime = None,
                       realised_pl: float = None,
                       account_value: float = None,
                       trading_platform: Broker = None):
        super().__init__()
        
        self.__start_year_date = start_year_date
        self.__end_year_date = end_year_date
        self.__realised_pl = realised_pl
        self.__account_value = account_value
        self.__trading_platform = trading_platform
        
        realised_pl_display = f'${realised_pl}' if realised_pl >= 0 else f'-${abs(realised_pl)}'

        embed = discord.Embed(title=f'Yearly Realised Profit and Loss from {start_year_date.strftime("%Y-%m-%d")} to {end_year_date.strftime("%Y-%m-%d")}\n') 
        embed.add_field(name = 'Realised:', value=f'{realised_pl_display}', inline=True)
        
        if account_value:
            account_growth_display = round((realised_pl/ (account_value - realised_pl)) * 100, 1)
            embed.add_field(name = 'Account Growth(%):', value=f'{account_growth_display}', inline=False)
        
        if trading_platform:
            embed.add_field(name = 'Trading Platform:', value=f'{trading_platform.value}', inline=False)        
        
        self.embed = embed

    def __members(self):
        return (self.__start_year_date, self.__end_year_date,
                self.__realised_pl, self.__account_value,
                self.__trading_platform)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, YearlyProfitAndLoss):
            return self.__members() == other.__members()

    def __hash__(self) -> int:
        return hash(self.__members())

    @property
    def start_year_date(self):
        return self.__start_year_date
    
    @start_year_date.setter
    def start_year_date(self, start_year_date):
        self.__start_year_date = start_year_date
        
    @property
    def end_year_date(self):
        return self.__end_year_date
    
    @end_year_date.setter
    def end_year_date(self, end_year_date):
        self.__end_year_date = end_year_date
        
    @property
    def realised_pl(self):
        return self.__realised_pl
    
    @realised_pl.setter
    def realised_pl(self, realised_pl):
        self.__realised_pl = realised_pl

    @property
    def account_value(self):
        return self.__account_value
    
    @account_value.setter
    def account_value(self, account_value):
        self.__account_value = account_value
        
    @property
    def trading_platform(self):
        return self.__trading_platform
    
    @trading_platform.setter
    def trading_platform(self, trading_platform):
        self.__trading_platform = trading_platform