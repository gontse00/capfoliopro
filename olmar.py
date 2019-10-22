#On-Line Portfolio Moving Average Reversion
import numpy as np 
import os
import pandas as pd
import pytz
from collections import OrderedDict
import zipline
from datetime import datetime
from zipline.finance import commission, slippage
from zipline.api import order, order_target_percent, symbol, record, set_benchmark
#import pandas_datareader as web
import yfinance as yf

def backtest_olmar(STOCKS):
	df_dict = OrderedDict()
	for ticker in STOCKS:
		#df = web.DataReader(ticker, "yahoo", start = datetime(2016,1,1,0,0,0,0))
		#df = web.DataReader(ticker, 'yahoo', start=datetime(2015,1,1,0,0,0,0), end=datetime.today())["Close"]
		ticker_df = yf.Ticker(ticker)
		df = ticker_df.history(period="5y")
		df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
		df_dict[ticker] = df
	data = pd.Panel(df_dict)

	def initialize(algo, eps=1, window_length=5):
	    algo.stocks = STOCKS
	    algo.tickers = [symbol(ticker) for ticker in algo.stocks]
	    algo.m = len(algo.stocks)
	    algo.price = {}
	    algo.b_t = np.ones(algo.m)/algo.m
	    algo.eps = eps
	    algo.window_length = window_length

	    algo.set_commission(commission.PerShare(cost=0))
	    algo.set_slippage(slippage.FixedSlippage(spread=0))
	def handle_data(algo, data):
	    m = algo.m
	    x_tilde = np.zeros(m)
	    b = np.zeros(m)

	    #moving average price for each asset
	    mavgs = data.history(algo.tickers, 'price', algo.window_length, '1d').mean()
	    for i, ticker in enumerate(algo.tickers):
		    price = data.current(symbol(ticker.symbol), "price")
		    x_tilde[i] = mavgs[ticker]/price

	    #olmar algo 2
	    x_bar = x_tilde.mean()
	    #market relative deviation
	    mar_rel_dev = x_tilde - x_bar
	    #expected return with current portflio
	    exp_return = np.dot(algo.b_t, x_tilde)
	    weight = algo.eps - exp_return
	    variability = (np.linalg.norm(mar_rel_dev))**2

	    if variability == 0.0:
		    step_size = 0
	    else:
		    step_size=max(0, weight/variability)

	    b = algo.b_t + step_size*mar_rel_dev
	    b_norm = simplex_projection(b)
	    np.testing.assert_almost_equal(b_norm.sum(), 1)

	    rebalance_portfolio(algo, data, b_norm)
	    algo.b_t = b_norm
	def rebalance_portfolio(algo, data, desired_port):
	    #rebalance portfolio
	    for i, ticker in enumerate(algo.tickers):
		    algo.order_target_percent(symbol(ticker.symbol), desired_port[i])
	def simplex_projection(v, b=1):
	    v = np.asarray(v)
	    p = len(v)
	    v = (v>0)*v
	    u = np.sort(v)[::-1]
	    sv = np.cumsum(u)

	    rho = np.where(u>(sv-b)/np.arange(1,p+1))[0][-1]
	    theta = np.max([0, (sv[rho]-b)/(rho+1)])
	    w = (v-theta)
	    w[w<0]=0
	    return w

	portfolio =  zipline.run_algorithm(data=data, 
		start=datetime(2016,1,15,0,0,0,0,pytz.utc),
		end=datetime(2019,6,1,0,0,0,0,pytz.utc),
		initialize=initialize,
	    capital_base = 100000.0,
	    handle_data = handle_data)
	return portfolio
#portfolio.to_pickle(portfolio, os.path.join(os.getcwd(), "data/backtest_results.pickle"), compression=None)
#import pyfolio as pf 
#returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(portfolio)
#pf.create_full_tear_sheet(returns, positions=positions, transactions=transactions, round_trips=True)
#tickers = ["AAPL", "AMZN"]
#portfolio = backtest_olmar(tickers)
