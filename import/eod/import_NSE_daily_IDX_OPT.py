from datascrapper import nse_urls
from config.postgres_connection import session
from model.nse_indices_option_daily import NseIndicesOptionDaily
from nsepy import get_history
from datetime import date
from model.stock_list import StockList
from datascrapper import nse_utils
import time
from datetime import datetime
import asyncio
import json

start = time.process_time()
trade_date = datetime.today()


def cleanupOldFnOData():
    session.query(NseIndicesOptionDaily.expiry_date < trade_date).delete()
    session.commit()


stocks = session.query(StockList).filter(StockList.downloaded == False,StockList.fno == True,StockList.indices == True)
for stock in stocks:
	print("######################## Running for Stock:" + stock.stock_code)
	start = time.process_time()
	option_chain = nse_urls.get_incices_opt_chain_url(stock.stock_code).text
	option_chain_json = json.loads(option_chain)
	#print(option_chain_json)
	#ce_values = [ceData for ceData in option_chain_json["filtered"]["data"][1]["CE"]]
	#session.bulk_insert_mappings()
	for option_data in option_chain_json["records"]["data"]:
		if 'CE' in option_data:
			ce_value = option_data['CE']
			#print(ce_value)
			stock_ce_option = NseIndicesOptionDaily(stock_id=stock.stock_id, trade_date=trade_date,
											   stock_code=stock.stock_code, strike_price=ce_value['strikePrice'],
											   option_type='CE',expiry_date=ce_value['expiryDate'],identifier=ce_value['identifier'],
											   open_interest=ce_value['openInterest'],change_in_oi=ce_value['changeinOpenInterest'],
											   percent_change_in_oi=ce_value['changeinOpenInterest'],total_traded_volume=ce_value['totalTradedVolume'],
											   implied_volatility=ce_value['impliedVolatility'],last_price=ce_value['lastPrice'],change=ce_value['change'],
											   total_buy_quantity=ce_value['totalBuyQuantity'],total_sell_quantity=ce_value['totalSellQuantity'],
											   underlying_value=ce_value['underlyingValue'])
			#print(stock_ce_option)
			session.add(stock_ce_option)
		if 'PE' in option_data:
			pe_value = option_data['PE']
			stock_pe_option = NseIndicesOptionDaily(stock_id=stock.stock_id, trade_date=trade_date,
											   stock_code=stock.stock_code, strike_price=pe_value['strikePrice'],
											   option_type='PE', expiry_date=pe_value['expiryDate'],
											   identifier=pe_value['identifier'],
											   open_interest=pe_value['openInterest'],
											   change_in_oi=pe_value['changeinOpenInterest'],
											   percent_change_in_oi=pe_value['changeinOpenInterest'],
											   total_traded_volume=pe_value['totalTradedVolume'],
											   implied_volatility=pe_value['impliedVolatility'],
											   last_price=pe_value['lastPrice'], change=ce_value['change'],
											   total_buy_quantity=pe_value['totalBuyQuantity'],
											   total_sell_quantity=pe_value['totalSellQuantity'],
											   underlying_value=pe_value['underlyingValue'])
			#print(stock_pe_option)
			session.add(stock_pe_option)
		#stock_option = NseStockOptionDaily(stock_id=stock.stock_id,trade_date=trade_date,stock_code=stock.stock_code,strike_price=)
		#print(ce_value["PE"])

	session.commit()
	stocktoupdate = session.query(StockList).filter(StockList.stock_code == stock.stock_code).update(
		{StockList.downloaded: True}, synchronize_session=False)
	session.commit()


session.query(StockList).update({StockList.downloaded:False},synchronize_session=False)
session.commit()

print("Download Complete Option Data for all FNO Stocks")

