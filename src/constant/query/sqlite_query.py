from enum import Enum

class SqliteQuery(str, Enum):
    CHECK_PATTERN_ANALYSIS_MESSAGE_EXIST_QUERY = "SELECT * FROM pattern_analysis WHERE EXISTS (SELECT 1 FROM pattern_analysis WHERE ticker = ? AND hit_scanner_datetime = ? AND scan_pattern = ? AND bar_size = ?)"
    ADD_PATTERN_ANALYSIS_QUERY = "INSERT INTO pattern_analysis VALUES(?, ?, ?, ?)"
    DELETE_ALL_PATTERN_ANALYSIS_MESSAGE_QUERY = "DELETE FROM pattern_analysis"
    ADD_TRADE_SUMMARY_MESSAGE_QUERY = "INSERT INTO trade_summary VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    DELETE_ALL_TRADE_SUMMARY_MESSAGE_QUERY = "DELETE FROM trade_summary"
    CHECK_TRADE_SUMMARY_MESSAGE_EXIST_QUERY = "SELECT * FROM trade_summary WHERE EXISTS (SELECT 1 FROM trade_summary WHERE symbol = ? AND acquired_date = ? AND sold_date = ? AND trading_platform = ?)"
    CHECK_INTEREST_HISTORY_MESSAGE_EXIST_QUERY = "SELECT * FROM interest_history WHERE EXISTS (SELECT 1 FROM interest_history WHERE settle_date = ? AND trading_platform = ?)"
    ADD_INTEREST_HISTORY_MESSAGE_QUERY = "INSERT INTO interest_history VALUES(?, ?, ?)"
    DELETE_ALL_INTEREST_HISTORY_MESSAGE_QUERY = "DELETE FROM interest_history"
    CHECK_DAILY_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM daily_realised_pl WHERE EXISTS (SELECT 1 FROM daily_realised_pl WHERE settle_date = ? AND trading_platform = ?)"
    ADD_DAILY_REALISED_PL_MESSAGE_QUERY = "INSERT INTO daily_realised_pl VALUES(?, ?, ?)"
    DELETE_ALL_DAILY_REALISED_PL_MESSAGE_QUERY = "DELETE FROM daily_realised_pl"
    CHECK_WEEKLY_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM weekly_realised_pl WHERE EXISTS (SELECT 1 FROM weekly_realised_pl WHERE start_week_date = ? AND end_week_date = ? AND trading_platform = ?)"
    ADD_WEEKLY_REALISED_PL_MESSAGE_QUERY = "INSERT INTO weekly_realised_pl VALUES(?, ?, ?, ?)"
    DELETE_ALL_WEEKLY_REALISED_PL_MESSAGE_QUERY = "DELETE FROM weekly_realised_pl"
    CHECK_MONTH_TO_DATE_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM month_to_date_realised_pl WHERE EXISTS (SELECT 1 FROM month_to_date_realised_pl WHERE settle_date = ? AND trading_platform = ?)"
    ADD_MONTH_TO_DATE_REALISED_PL_MESSAGE_QUERY = "INSERT INTO month_to_date_realised_pl VALUES(?, ?, ?)"    
    DELETE_ALL_MONTH_TO_DATE_REALISED_PL_MESSAGE_QUERY = "DELETE FROM month_to_date_realised_pl"
    CHECK_YEAR_TO_DATE_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM year_to_date_realised_pl WHERE EXISTS (SELECT 1 FROM year_to_date_realised_pl WHERE settle_date = ? AND trading_platform = ?)"
    ADD_YEAR_TO_DATE_REALISED_PL_MESSAGE_QUERY = "INSERT INTO year_to_date_realised_pl VALUES(?, ?, ?)"    
    DELETE_ALL_YEAR_TO_DATE_REALISED_PL_MESSAGE_QUERY = "DELETE FROM year_to_date_realised_pl"
    CHECK_MONTHLY_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM monthly_realised_pl WHERE EXISTS (SELECT 1 FROM monthly_realised_pl WHERE start_month_date = ? AND end_month_date = ? AND trading_platform = ?)"
    ADD_MONTHLY_REALISED_PL_MESSAGE_QUERY = "INSERT INTO monthly_realised_pl VALUES(?, ?, ?, ?)"
    DELETE_ALL_MONTHLY_REALISED_PL_MESSAGE_QUERY = "DELETE FROM monthly_realised_pl"
    CHECK_YEARLY_REALISED_PL_MESSAGE_EXIST_QUERY = "SELECT * FROM yearly_realised_pl WHERE EXISTS (SELECT 1 FROM yearly_realised_pl WHERE start_year_date = ? AND end_year_date = ? AND trading_platform = ?)"
    ADD_YEARLY_REALISED_PL_MESSAGE_QUERY = "INSERT INTO yearly_realised_pl VALUES(?, ?, ?, ?)"
    DELETE_ALL_YEARLY_REALISED_PL_MESSAGE_QUERY = "DELETE FROM yearly_realised_pl"
    CHECK_IMPORT_PL_FILE_MESSAGE_EXIST_QUERY = "SELECT * FROM import_pl_file WHERE EXISTS (SELECT 1 FROM import_pl_file WHERE start_date = ? AND end_date = ? AND filename = ? AND type = ? )"
    ADD_IMPORT_PL_FILE_MESSAGE_QUERY = "INSERT INTO import_pl_file VALUES(?, ?, ?, ?)"
    DELETE_ALL_IMPORT_PL_FILE_MESSAGE_QUERY = "DELETE FROM import_pl_file"
    GET_SEND_AGGREGATED_DAILY_REALISED_PL_QUERY = '''
        SELECT daily_realised_pl.settle_date, 
               sum(daily_realised_pl.realised_pl) AS realised_pl, 
               aggregated_daily_reliased_pl.settle_date 
        FROM daily_realised_pl
        LEFT JOIN aggregated_daily_reliased_pl
            ON daily_realised_pl.settle_date = aggregated_daily_reliased_pl.settle_date
        GROUP BY daily_realised_pl.settle_date, aggregated_daily_reliased_pl.settle_date
        HAVING aggregated_daily_reliased_pl.settle_date IS NULL
        ORDER BY daily_realised_pl.settle_date'''
    GET_SEND_AGGREGATED_WEEKLY_REALISED_PL_QUERY = '''
        SELECT weekly_realised_pl.start_week_date, 
               weekly_realised_pl.end_week_date, 
               sum(weekly_realised_pl.realised_pl) AS realised_pl, 
               aggregated_weekly_realised_pl.start_week_date, 
               aggregated_weekly_realised_pl.end_week_date 
        FROM weekly_realised_pl
        LEFT JOIN aggregated_weekly_realised_pl
            ON weekly_realised_pl.start_week_date = aggregated_weekly_realised_pl.start_week_date
                AND weekly_realised_pl.end_week_date = aggregated_weekly_realised_pl.end_week_date
        GROUP BY weekly_realised_pl.start_week_date, weekly_realised_pl.end_week_date, 
                aggregated_weekly_realised_pl.start_week_date, aggregated_weekly_realised_pl.end_week_date
        HAVING aggregated_weekly_realised_pl.start_week_date IS NULL 
            AND aggregated_weekly_realised_pl.end_week_date IS NULL
            ORDER BY weekly_realised_pl.start_week_date, weekly_realised_pl.end_week_date'''
    GET_SEND_AGGREGATED_MONTH_TO_DATE_REALISED_PL_QUERY = '''
        SELECT month_to_date_realised_pl.settle_date, 
               sum(month_to_date_realised_pl.realised_pl) AS realised_pl, 
               aggregated_month_to_date_realised_pl.settle_date 
        FROM month_to_date_realised_pl
        LEFT JOIN aggregated_month_to_date_realised_pl
           ON month_to_date_realised_pl.settle_date = aggregated_month_to_date_realised_pl.settle_date
        GROUP BY month_to_date_realised_pl.settle_date, aggregated_month_to_date_realised_pl.settle_date
        HAVING aggregated_month_to_date_realised_pl.settle_date IS NULL
        ORDER BY month_to_date_realised_pl.settle_date'''
    GET_SEND_AGGREGATED_YEAR_TO_DATE_REALISED_PL_QUERY = '''
        SELECT year_to_date_realised_pl.settle_date, 
               sum(year_to_date_realised_pl.realised_pl) AS realised_pl, 
               aggregated_year_to_date_realised_pl.settle_date 
        FROM year_to_date_realised_pl
        LEFT JOIN aggregated_year_to_date_realised_pl
            ON year_to_date_realised_pl.settle_date = aggregated_year_to_date_realised_pl.settle_date
        GROUP BY year_to_date_realised_pl.settle_date, aggregated_year_to_date_realised_pl.settle_date
        HAVING aggregated_year_to_date_realised_pl.settle_date IS NULL
        ORDER BY year_to_date_realised_pl.settle_date'''
    GET_SEND_AGGREGATED_MONTHLY_REALISED_PL_EXIST_QUERY = '''
        SELECT monthly_realised_pl.start_month_date, 
               monthly_realised_pl.end_month_date, 
               sum(monthly_realised_pl.realised_pl) AS realised_pl, 
               aggregated_monthly_realised_pl.start_month_date, 
               aggregated_monthly_realised_pl.end_month_date 
        FROM monthly_realised_pl
        LEFT JOIN aggregated_monthly_realised_pl
            ON monthly_realised_pl.start_month_date = aggregated_monthly_realised_pl.start_month_date
                AND monthly_realised_pl.end_month_date = aggregated_monthly_realised_pl.end_month_date
        GROUP BY monthly_realised_pl.start_month_date, 
                 monthly_realised_pl.end_month_date, 
                 aggregated_monthly_realised_pl.start_month_date, 
                 aggregated_monthly_realised_pl.end_month_date
        HAVING aggregated_monthly_realised_pl.start_month_date IS NULL 
            AND aggregated_monthly_realised_pl.end_month_date IS NULL
        ORDER BY monthly_realised_pl.start_month_date, monthly_realised_pl.end_month_date'''
    GET_SEND_AGGREGATED_YEARLY_REALISED_PL_EXIST_QUERY = '''
        SELECT yearly_realised_pl.start_year_date, 
               yearly_realised_pl.end_year_date, 
               sum(yearly_realised_pl.realised_pl) AS realised_pl, 
               aggregated_yearly_realised_pl.start_year_date, 
               aggregated_yearly_realised_pl.end_year_date 
        FROM yearly_realised_pl
        LEFT JOIN aggregated_yearly_realised_pl
            ON yearly_realised_pl.start_year_date = aggregated_yearly_realised_pl.start_year_date
                AND yearly_realised_pl.end_year_date = aggregated_yearly_realised_pl.end_year_date
        GROUP BY yearly_realised_pl.start_year_date, 
                 yearly_realised_pl.end_year_date, 
                 aggregated_yearly_realised_pl.start_year_date, 
                 aggregated_yearly_realised_pl.end_year_date
        HAVING aggregated_yearly_realised_pl.start_year_date IS NULL 
            AND aggregated_yearly_realised_pl.end_year_date IS NULL
        ORDER BY yearly_realised_pl.start_year_date, yearly_realised_pl.end_year_date'''
    ADD_AGGREGATED_DAILY_REALISED_PL_QUERY = "INSERT INTO aggregated_daily_reliased_pl VALUES(?, ?)"
    ADD_AGGREGATED_WEEKLY_REALISED_PL_QUERY = "INSERT INTO aggregated_weekly_realised_pl VALUES(?, ?, ?)"
    ADD_AGGREGATED_MONTH_TO_DATE_REALISED_PL_QUERY = "INSERT INTO aggregated_month_to_date_realised_pl VALUES(?, ?)"
    ADD_AGGREGATED_YEAR_TO_DATE_REALISED_PL_QUERY = "INSERT INTO aggregated_year_to_date_realised_pl VALUES(?, ?)"
    ADD_AGGREGATED_MONTHLY_REALISED_PL_QUERY = "INSERT INTO aggregated_monthly_realised_pl VALUES(?, ?, ?)"
    ADD_AGGREGATED_YEARLY_REALISED_PL_QUERY = "INSERT INTO aggregated_yearly_realised_pl VALUES(?, ?, ?)"
    DELETE_ALL_AGGREGATED_DAILY_REALISED_PL_QUERY = 'DELETE FROM aggregated_daily_reliased_pl'
    DELETE_ALL_AGGREGATED_WEEKLY_REALISED_PL_QUERY = 'DELETE FROM aggregated_weekly_realised_pl'
    DELETE_ALL_AGGREGATED_MONTH_TO_DATE_REALISED_PL_QUERY = 'DELETE FROM aggregated_month_to_date_realised_pl'
    DELETE_ALL_AGGREGATED_YEAR_TO_DATE_REALISED_PL_QUERY = 'DELETE FROM aggregated_year_to_date_realised_pl'
    DELETE_ALL_AGGREGATED_MONTHLY_REALISED_PL_QUERY = 'DELETE FROM aggregated_monthly_realised_pl'
    DELETE_ALL_AGGREGATED_YEARLY_REALISED_PL_QUERY = 'DELETE FROM aggregated_yearly_realised_pl'
    ADD_DAY_TRADE_SUMMARY_QUERY = "INSERT INTO aggregated_yearly_realised_pl VALUES(?, ?, ?)"
    GET_PREVIOUS_DAY_TOP_GAINER_QUERY = 'SELECT * FROM top_gainer_history WHERE percentage >= ? AND scan_date >= ? AND scan_date <= ? ORDER BY scan_date, percentage DESC'
    GET_OFFERING_HISTORY_QUERY = 'SELECT * FROM offering_history WHERE ticker = ?'
    GET_LATEST_TICKER_SCRAPE_DATE_QUERY = 'SELECT scrape_date FROM offering_history WHERE ticker = ? ORDER BY scrape_date DESC LIMIT 1'