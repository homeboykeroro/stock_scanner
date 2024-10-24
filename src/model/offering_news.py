from itertools import islice


class OfferingNews:
    MAX_DISPLAY_RESULT = 3
    
    def __init__(self, symbol: str, 
                 date_to_news_dict: dict,
                 max_offering_news_size: int):
        self.__symbol = symbol
        self.__date_to_news_dict = date_to_news_dict
        self.__max_offering_news_size = max_offering_news_size
    
    def __members(self):
        return (self.__symbol, self.__date_to_news_dict)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OfferingNews):
            return self.__members() == other.__members()

    def __hash__(self) -> int:
        return hash(self.__members())

    def add_offering_news_to_embed_msg(self, embed):
        #https://stackoverflow.com/questions/54753005/is-there-any-way-to-embed-a-hyperlink-in-a-richembed
        if not self.__date_to_news_dict:
            embed.add_field(name = f'\nOffering History Data Not Found', value='\u200b', inline = False)    
            return
        
        if self.__date_to_news_dict == 'error':
            embed.add_field(name = f'\nOffering History Data Not Available Due to Fatal Error', value='\u200b', inline = False)    
            return
        
        offering_news_dict = self.__date_to_news_dict
        
        if self.__max_offering_news_size is not None and self.__date_to_news_dict is not None:
            truncated_items = list(self.__date_to_news_dict.items())[-self.__max_offering_news_size:]
            offering_news_dict = dict(truncated_items)
                
        concat_str = ''
        for publish_date, news in offering_news_dict.items():
            concat_str += f"[{news.get('title')} - ({publish_date.strftime('%Y-%m-%d')})]({news.get('shortened_url')})\n"
            
        embed.add_field(name = f'\nOffering History:', value=concat_str, inline = False)
        
