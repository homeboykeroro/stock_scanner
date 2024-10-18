-- Create common user (which has the same identity across all containers)
CREATE USER C##demo IDENTIFIED BY demo
DEFAULT TABLESPACE USERS



--------------------------------------------------------
--  DDL for Table PATTERN_ANALYSIS
--------------------------------------------------------

  CREATE TABLE "PATTERN_ANALYSIS" 
   (	"TICKER" VARCHAR2(4 BYTE), 
	"HIT_SCANNER_DATETIME" TIMESTAMP (6), 
	"SCAN_PATTERN" VARCHAR2(50 BYTE), 
	"BAR_SIZE" VARCHAR2(10 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table PATTERN_ANALYSIS
--------------------------------------------------------

  ALTER TABLE "PATTERN_ANALYSIS" MODIFY ("TICKER" NOT NULL ENABLE);
  ALTER TABLE "PATTERN_ANALYSIS" MODIFY ("HIT_SCANNER_DATETIME" NOT NULL ENABLE);
  ALTER TABLE "PATTERN_ANALYSIS" MODIFY ("SCAN_PATTERN" NOT NULL ENABLE);
  ALTER TABLE "PATTERN_ANALYSIS" MODIFY ("BAR_SIZE" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table TOP_GAINER_HISTORY
--------------------------------------------------------

  CREATE TABLE "TOP_GAINER_HISTORY" 
   (	"TICKER" VARCHAR2(4 BYTE), 
	"COMPANY" VARCHAR2(200 BYTE), 
	"SECTOR" VARCHAR2(100 BYTE), 
	"INDUSTRY" VARCHAR2(100 BYTE), 
	"SCAN_DATE" TIMESTAMP (6), 
	"PRICE" FLOAT(126), 
	"VOLUME" NUMBER, 
	"PERCENTAGE" FLOAT(126), 
	"MARKET_CAP" NUMBER, 
	"COUNTRY" VARCHAR2(50 BYTE)
   ) SEGMENT CREATION IMMEDIATE 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table TOP_GAINER_HISTORY
--------------------------------------------------------

  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("TICKER" NOT NULL ENABLE);
  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("COMPANY" NOT NULL ENABLE);
  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("SCAN_DATE" NOT NULL ENABLE);
  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("PRICE" NOT NULL ENABLE);
  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("VOLUME" NOT NULL ENABLE);
  ALTER TABLE "TOP_GAINER_HISTORY" MODIFY ("PERCENTAGE" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table TRADE_SUMMARY
--------------------------------------------------------

  CREATE TABLE "TRADE_SUMMARY" 
   (	"TICKER" VARCHAR2(4 BYTE), 
	"ACQUIRED_DATE" TIMESTAMP (6), 
	"SOLD_DATE" TIMESTAMP (6), 
	"AVG_ENTRY_PRICE" FLOAT(126), 
	"AVG_EXIT_PRICE" FLOAT(126), 
	"REALISED_PL" FLOAT(126), 
	"REALISED_PL_PERCENT" FLOAT(126), 
	"COMPANY_NAME" VARCHAR2(200 BYTE), 
	"SECTOR" VARCHAR2(100 BYTE), 
	"MARKET_CAP" NUMBER, 
	"SHORTABLE" VARCHAR2(20 BYTE), 
	"SHORTABLE_SHARES" NUMBER, 
	"REBATE_RATE" FLOAT(126), 
	"TRADING_PLATOFRM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table TRADE_SUMMARY
--------------------------------------------------------

  ALTER TABLE "TRADE_SUMMARY" MODIFY ("TICKER" NOT NULL ENABLE);
  ALTER TABLE "TRADE_SUMMARY" MODIFY ("ACQUIRED_DATE" NOT NULL ENABLE);
  ALTER TABLE "TRADE_SUMMARY" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "TRADE_SUMMARY" MODIFY ("REALISED_PL_PERCENT" NOT NULL ENABLE);
  ALTER TABLE "TRADE_SUMMARY" MODIFY ("TRADING_PLATOFRM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_DAILY_RELIASED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_DAILY_RELIASED_PL" 
   (	"SETTLE_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_DAILY_RELIASED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_DAILY_RELIASED_PL" MODIFY ("SETTLE_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_DAILY_RELIASED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_MONTH_TO_DATE_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_MONTH_TO_DATE_REALISED_PL" 
   (	"START_MONTH_DATE" TIMESTAMP (6), 
	"END_MONTH_DATE" TIMESTAMP (6), 
	"REALISED_PL" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_MONTH_TO_DATE_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_MONTH_TO_DATE_REALISED_PL" MODIFY ("START_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_MONTH_TO_DATE_REALISED_PL" MODIFY ("END_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_MONTH_TO_DATE_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_YEAR_TO_DATE_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_YEAR_TO_DATE_REALISED_PL" 
   (	"SETTLE_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_YEAR_TO_DATE_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_YEAR_TO_DATE_REALISED_PL" MODIFY ("SETTLE_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_YEAR_TO_DATE_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_WEEKLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_WEEKLY_REALISED_PL" 
   (	"START_WEEK_DATE" TIMESTAMP (6), 
	"END_WEEK_DATE" TIMESTAMP (6), 
	"REALISED_PL" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_WEEKLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_WEEKLY_REALISED_PL" MODIFY ("START_WEEK_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_WEEKLY_REALISED_PL" MODIFY ("END_WEEK_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_WEEKLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_MONTHLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_MONTHLY_REALISED_PL" 
   (	"START_MONTH_DATE" TIMESTAMP (6), 
	"END_MONTH_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_MONTHLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_MONTHLY_REALISED_PL" MODIFY ("START_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_MONTHLY_REALISED_PL" MODIFY ("END_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_MONTHLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table AGGREGATED_YEARLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "AGGREGATED_YEARLY_REALISED_PL" 
   (	"START_YEAR_DATE" TIMESTAMP (6), 
	"END_YEAR_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table AGGREGATED_YEARLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "AGGREGATED_YEARLY_REALISED_PL" MODIFY ("START_YEAR_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_YEARLY_REALISED_PL" MODIFY ("END_YEAR_DATE" NOT NULL ENABLE);
  ALTER TABLE "AGGREGATED_YEARLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table DAILY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "DAILY_REALISED_PL" 
   (	"SETTLE_DATE" TIMESTAMP (6), 
	"REALIZED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table DAILY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "DAILY_REALISED_PL" MODIFY ("SETTLE_DATE" NOT NULL ENABLE);
  ALTER TABLE "DAILY_REALISED_PL" MODIFY ("REALIZED_PL" NOT NULL ENABLE);
  ALTER TABLE "DAILY_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table MONTH_TO_DATE_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "MONTH_TO_DATE_REALISED_PL" 
   (	"SETTLE_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table MONTH_TO_DATE_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "MONTH_TO_DATE_REALISED_PL" MODIFY ("SETTLE_DATE" NOT NULL ENABLE);
  ALTER TABLE "MONTH_TO_DATE_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "MONTH_TO_DATE_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table YEAR_TO_DATE_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "YEAR_TO_DATE_REALISED_PL" 
   (	"SETTLE_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table YEAR_TO_DATE_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "YEAR_TO_DATE_REALISED_PL" MODIFY ("SETTLE_DATE" NOT NULL ENABLE);
  ALTER TABLE "YEAR_TO_DATE_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "YEAR_TO_DATE_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table WEEKLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "WEEKLY_REALISED_PL" 
   (	"START_WEEK_DATE" TIMESTAMP (6), 
	"END_WEEK_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table WEEKLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "WEEKLY_REALISED_PL" MODIFY ("START_WEEK_DATE" NOT NULL ENABLE);
  ALTER TABLE "WEEKLY_REALISED_PL" MODIFY ("END_WEEK_DATE" NOT NULL ENABLE);
  ALTER TABLE "WEEKLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "WEEKLY_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table MONTHLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "MONTHLY_REALISED_PL" 
   (	"START_MONTH_DATE" TIMESTAMP (6), 
	"END_MONTH_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table MONTHLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "MONTHLY_REALISED_PL" MODIFY ("START_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "MONTHLY_REALISED_PL" MODIFY ("END_MONTH_DATE" NOT NULL ENABLE);
  ALTER TABLE "MONTHLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "MONTHLY_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);



--------------------------------------------------------
--  DDL for Table YEARLY_REALISED_PL
--------------------------------------------------------

  CREATE TABLE "YEARLY_REALISED_PL" 
   (	"START_YEAR_DATE" TIMESTAMP (6), 
	"END_YEAR_DATE" TIMESTAMP (6), 
	"REALISED_PL" FLOAT(126), 
	"TRADING_PLATFORM" VARCHAR2(20 BYTE)
   ) SEGMENT CREATION DEFERRED 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table YEARLY_REALISED_PL
--------------------------------------------------------

  ALTER TABLE "YEARLY_REALISED_PL" MODIFY ("START_YEAR_DATE" NOT NULL ENABLE);
  ALTER TABLE "YEARLY_REALISED_PL" MODIFY ("END_YEAR_DATE" NOT NULL ENABLE);
  ALTER TABLE "YEARLY_REALISED_PL" MODIFY ("REALISED_PL" NOT NULL ENABLE);
  ALTER TABLE "YEARLY_REALISED_PL" MODIFY ("TRADING_PLATFORM" NOT NULL ENABLE);




--------------------------------------------------------
--  DDL for Table IB_API_ENDPOINT_LOCK
--------------------------------------------------------
CREATE TABLE "API_ENDPOINT_LOCK" 
(
    "ENDPOINT" VARCHAR2(50 BYTE) NOT NULL,
    "IS_LOCKED" CHAR(1 BYTE) CHECK ("IS_LOCKED" IN ('Y', 'N')) NOT NULL,
    "LOCKED_BY" VARCHAR2(20 BYTE),
    "LOCK_DATETIME" TIMESTAMP (6) DEFAULT CURRENT_TIMESTAMP
) SEGMENT CREATION DEFERRED 
PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
NOCOMPRESS LOGGING
TABLESPACE "USERS";

INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/scanner/params', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/auth/status', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/scanner/run', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/marketdata/history', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/accounts', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/trsrv/secdef', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/marketdata/snapshot', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/trsrv/stocks', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/sso/validate', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/reauthenticate', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/portfolio/accounts', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/portfolio/subaccounts', 'N', NULL, NULL);
INSERT INTO API_ENDPOINT_LOCK (ENDPOINT, IS_LOCKED, LOCKED_BY, LOCK_DATE) VALUES ('/iserver/account/trades', 'N', NULL, NULL);
