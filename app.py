import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_table as dt
import pandas as pd 
import numpy as np 
import pandas_datareader as web
import os
import copy
from datetime import datetime
import plotly.graph_objects as go
import plotly.figure_factory as ff
from collections import OrderedDict
import pytz
from olmar import backtest_olmar
import pyfolio as pf
import json
import empyrical as ep
import dash_bootstrap_components as dbc
import yfinance as yf
import dash_daq as daq

stock_data = pd.read_csv(os.path.join(os.getcwd(),'data/new_stock_data.csv'))
stock_data.index = stock_data["symbol"]
dropdown_options = [{'label':stock_data['name'][i], 'value':stock_data['symbol'][i]} for i in range(0,len(stock_data))]
stock_data.index = stock_data["symbol"]
stock_data.drop("symbol", axis=1)
benchmark = yf.Ticker("^GSPC")
benchmark_df = benchmark.history(period="5y")["Close"]
factor_returns = ep.simple_returns(benchmark_df)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://codepen.io/chriddyp/pen/brPBPO.css']

layout = dict(
	color="green",
    autosize=True,
    automargin=True,
    height=250,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis1={"gridcolor": "rgb(215, 222, 217)", "zerolinecolor":"rgb(215, 222, 217)"},
    yaxis1={"gridcolor": "rgb(215, 222, 217)"},
    legend=dict(font=dict(size=10), orientation="h")
)

go_layout = go.Layout(
	autosize=True,
    height=250,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis1={"gridcolor":"rgb(215, 222, 217)", "zerolinecolor":"rgb(215, 222, 217)"},
    yaxis1={"gridcolor":"rgb(215, 222, 217)"},
    legend=dict(font=dict(size=10), orientation="h"))

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], 
	external_stylesheets = external_stylesheets)

server = app.server
app.title = "Capfolio"
app.layout = html.Div([
html.Title("Capfolio"),
html.Div(id="output-clientside"),

html.Div([
	html.Div([
		html.Div([
			html.H3("Porfolio Optimization & Risk Analysis",style={"marging-bottom":"0px", "text-align":"center"}),
			html.H5("An Event Driven Backtester",style = {"marging-top":"0px", "text-align":"center"})],
			    id = "title",style = {"marging-bottom":"25px"})]),
	######start tabs here
	dcc.Tabs(id="page-tabs",value="EXPLORE", mobile_breakpoint=0,parent_className="custom-tabs", colors={"border":"rgba(0,0,0,0)","background":"rgba(0,0,0,0)"},
		children=[
	    dcc.Tab(label="EXPLORE", value="EXPLORE", className="custom-tab", selected_className="custom-tab--selected",
		    children=[
		        html.Hr(),
	            html.Div([
    	            html.Div([
	                    dcc.Dropdown(id="ticker-names-dropdown",options=dropdown_options,value=stock_data['symbol'][0]),])], 
    	                    style = {"marging-bottom":"10px"}),        #1
                html.Div(id="ticker-info", style={"display":"none"}),  #2 

                html.Div([
		            

                    dcc.Tabs(id="tabs",mobile_breakpoint=0, value="overview", parent_className="custom-tabs",
        	            children=[
                            dcc.Tab(label="Overview", value="overview", 
                	            children=[
                		                html.Div([], ),
                		                html.Div([
                		            	    html.Div([
		                                        html.Div([
		                                            html.Div([
		                                                html.Div([
		        	                                        html.H5(id="name", style={"margin-bottom":"0px","color":"black"}),
		        	                                        html.H6(id="sector-industry", style={"marging-top":"0rem"})], className="ten columns"),
		        	                                    html.Div(html.Button('+ portfolio',id='add-ticker-but',n_clicks=0), style={"float":"right"}, 
		        		                            className="two columns dcc_control")], 
		        	                            style={"marging-top":"25px"} ,className="row"),
		                                        ])
		                                     ]),
                		            	html.Div([html.Div(id="previous-close")]),
                		            	
		        	                    dcc.Tabs(id="time-tabs", mobile_breakpoint=0, value="1-year-tab",parent_className="custom-tabs",
		        		                    children=[
		        		                        dcc.Tab(label="1D", value="1-day-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="5D", value="5-days-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="1M", value="1-month-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="6M", value="6-months-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="1Y", value="1-year-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="YTD", value="year-to-date", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="5Y", value="5-years-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="max", value="max", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),]
		        		                    , colors={"border":"rgba(0,0,0,0)","background":"rgba(0,0,0,0)"}),


		                                    html.Div(id="price-history-figure")
		                                ], className="pretty_container"),]
		                        , className="custom-tab", selected_className="custom-tab--selected"),

                	        dcc.Tab(label="News", value="news",
                		        children=[],className="custom-tab", selected_className="custom-tab--selected"),
                	        dcc.Tab(label="Financial Stats", value="financials", 
                		        children=[], className="custom-tab", selected_className="custom-tab--selected"),
                	        dcc.Tab(label="Similar", value="similar", 
                		        children=[], className="custom-tab", selected_className="custom-tab--selected")], 
                	        colors={"border":"rgba(0,0,0,0)","background":"rgba(0,0,0,0)"})
                    ])
                ]), 
	    dcc.Tab(label="PORTFOLIO", value="PORTFOLIO",
            children=[
                html.Hr(),
                html.Div([html.Div([dt.DataTable(id = "add-ticker",
                	columns=[{
                	            "name":"Ticker", "id":"ticker",
                	            "name":"Name", "id":"name",
                	            "name":"Sector", "id":"sector"}],data =[{}])])],style={"display":"none"}),
                html.Div(id="selected-portfolio"),
                dcc.Tabs(id="backtest-tabs", mobile_breakpoint=0, value="returns",parent_className="custom-tabs", colors={"border":"rgba(0,0,0,0)","background":"rgba(0,0,0,0)"},
                	children=[
                	    dcc.Tab(label="SUMMARY",value="summary", selected_className="custom-tab--selected",
                	    	children=[], className="custom-tab"),
                	    dcc.Tab(label="RETURNS", value="returns", selected_className="custom-tab--selected",
                		    children=[
                		        html.Div([
		                            html.Div([html.Div(id="returns-container")]),
		                            html.Div([html.Div(id="drawdown-container")]),
		                            ])], className="custom-tab"),
                	    dcc.Tab(label="POSITIONS", value="positions", selected_className="custom-tab--selected",
                		    children=[html.Div(id="positions")], className="custom-tab"),
                	    dcc.Tab(label="TRANSACTIONS", value="transactions", selected_className="custom-tab--selected",
                		    children=[], className="custom-tab"),
                	]),
                html.Div([html.Button('run backtest', id='run-backtest',n_clicks=0, style={"float":"right"})],
		             className="dcc_control", style = {"marging-bottom":"0px"}),
		    
	            html.Div(id="backtest-results", style={"display":"none"})], 
	        className="custom-tab", selected_className="custom-tab--selected")
	    ])######end tabs here                                               #3
    ]),
], style = {"width":"100%", "padding-left":"0%", "padding-right":"0%"})


#header conteny(Company name, sector, button and dropdown)

#callback to collect all ticker information including price history
@app.callback(Output("ticker-info","children"),
	[Input("ticker-names-dropdown","value")])
def collect_ticker_info(ticker):
	ticker_data = yf.Ticker(ticker)
	ticker_stats = ticker_data.info
	ticker_history = ticker_data.history(period="5y")["Close"]
	return [ticker_history.to_json(orient='split', date_format='iso'), str(ticker_stats)] 

@app.callback(
	[Output("name", "children"),
	Output("sector-industry", "children")],
	[Input("ticker-names-dropdown", "value")])
def get_company(ticker):
	company = stock_data.loc[ticker]
	sec_ind = html.H6(str(company["sector"])+" ("+str(company["industry"])+")")
	return company["name"], sec_ind

#Tabs(Overview, Financials, Comapare)
#@app.callback()
@app.callback(
	Output("price-history-figure","children"),
	[Input("ticker-info", "children"),
	 Input("time-tabs","value")])
def get_graph(ticker_info,tab):
	#data = yf.Ticker(ticker)
	#df = data.history(period="5y")["Close"]
	price = json.loads(ticker_info[0])
	price_index = price["index"]
	price_data = price["data"]
	a_data = price_data[-1:][0]-price_data[-30:-29][0]
	b_data = price_data[-1:][0]-price_data[-130:-129][0]
	c_data = price_data[-1:][0]-price_data[-260:-259][0]
	d_data = price_data[-1:][0]-price_data[1]

	m_figure = go.Figure(layout=go_layout)

	if tab=="1-month-tab" and a_data>0:
		m_figure.add_trace(go.Scatter(x=price_index[-30:],y=price_data[-30:],mode='lines',line=dict(color="green")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure
	elif tab=="1-month-tab" and a_data<0:
		m_figure.add_trace(go.Scatter(x=price_index[-30:],y=price_data[-30:],mode='lines',line=dict(color="red")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure

	if tab=="6-months-tab" and b_data>0:
		m_figure.add_trace(go.Scatter(x=price_index[-130:],y=price_data[-130:],mode='lines',line=dict(color="green")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure
	elif tab=="6-months-tab" and b_data<0:
		m_figure.add_trace(go.Scatter(x=price_index[-130:],y=price_data[-130:],mode='lines',line=dict(color="red")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure
	
	if tab=="1-year-tab" and c_data>0:
	    m_figure.add_trace(go.Scatter(x=price_index[-260:],y=price_data[-260:],mode='lines',line=dict(color="green")))
	    figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
	    return figure
	elif tab=="1-year-tab" and c_data<0:
		m_figure.add_trace(go.Scatter(x=price_index[-260:],y=price_data[-260:],mode='lines',line=dict(color="red")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure

	if tab=="5-years-tab" and d_data>0:
		m_figure.add_trace(go.Scatter(x=price_index,y=price_data,mode='lines',line=dict(color="green")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure
	elif tab=="5-years-tab" and d_data<0:
		m_figure.add_trace(go.Scatter(x=price_index,y=price_data,mode='lines',line=dict(color="red")))
		figure = dcc.Graph(id="price-history", figure=m_figure, config={'displayModeBar':False})
		return figure

@app.callback(
	Output("previous-close", "children"),
	[Input("ticker-info", "children")])
def get_keystats_table(ticker):
	ticker_stats = eval(ticker[1])
	rmc = np.round(ticker_stats['regularMarketChange'],4)
	rmcp = np.round(ticker_stats['regularMarketChangePercent'],4)


	if rmc > 0:
		rmc_tag = html.H6("+"+str(rmc)+"("+str(np.abs(rmcp))+"%"+")"+"\U00002191", style={"margin-top":"0px","color":"green"})
	else:
		rmc_tag = html.H6("-"+str(rmc)+"("+str(np.abs(rmcp))+"%"+")"+"\U00002193", style={"margin-top":"0px","color":"red"})

	if ticker_stats["marketCap"]>1000000 and ticker_stats["marketCap"]<1000000000:
		market_cap_ = round(ticker_stats["marketCap"]/1000000,1)
		market_cap_ = "$"+str(market_cap_)+"M"
	elif ticker_stats["marketCap"]>1000000000:
		market_cap_ = round(ticker_stats["marketCap"]/1000000000,1)
		market_cap_ = "$"+str(market_cap_)+"B"

	close_price = html.Div([
		html.Div([
			html.H6("$"+str(ticker_stats['regularMarketPreviousClose']), 
				style={"font-weight":"bold", "margin-bottom":"0px"}),
		    rmc_tag
		    ])], style={"margin-left":"0px", "margin-bottom":"0px"},className="price_mini_container")
	
	market_cap = html.Div([
		html.Div([
			html.H6(market_cap_, 
				style={"font-weight":"bold", "margin-bottom":"0px"}),
			html.H6("Market Cap",
				style={"margin-top":"0px"})])
		], style={"margin-bottom":"0px"},className="price_mini_container")

	dividend_yield = html.Div([
		html.Div([
			html.H6(str(round(ticker_stats["epsForward"],3)), 
				style={"font-weight":"bold", "margin-bottom":"0px"}),
			html.H6("EPS",
				style={"margin-top":"0px"})
			])
		],style={"margin-bottom":"0px"}, className="price_mini_container")

	price_earning = html.Div([
		html.Div([
			html.H6(round(ticker_stats["forwardPE"],3), 
				style={"font-weight":"bold", "margin-bottom":"0px"}),
			html.H6("PE", 
				style={"margin-top":"0px"})
			])
		],style={"margin-bottom":"0px"}, className="price_mini_container")

	return html.Div([
		close_price, 
		market_cap, 
		dividend_yield, 
		price_earning],className="row container-display")


@app.callback(
	[Output("add-ticker","data"),
	 Output("selected-portfolio","children")],
	[Input("add-ticker-but", "n_clicks"),
	Input("ticker-names-dropdown", "value")],
	[State("add-ticker", "data")])
def add_row(n_clicks, new_ticker, tickers_list):
	if n_clicks == 1:
		if {"ticker":new_ticker} not in tickers_list:
			#print(stock_data.loc[new_ticker])
			tickers_list.append(
				{
				    "ticker":new_ticker, 
				    "name":stock_data.loc[new_ticker]["name"],
				    "sector":stock_data.loc[new_ticker]["sector"]
				    })
			portfolio_table = dt.DataTable(
				columns=[
				    {"name":"Ticker", "id":"ticker"},
				    {"name":"Name", "id":"name"},
				    {"name":"Sector", "id":"sector"}],
		    	data=tickers_list[1:], 
		    	style_cell={"minWidth":"75px", 
		        "textAlign":"left",
		        'boxShadow': "0 0",
		        "backgroundColor":"rgba(0,0,0,0)",
		        "border":"0px 0px 0px 0px"},
		        style_data={"border":"rgba(0,0,0,0)"}, style_header={"border":"rgba(0,0,0,0)"})
			return [tickers_list, portfolio_table]
	else:raise PreventUpdate

@app.callback(Output("add-ticker-but", "n_clicks"), 
	[Input("ticker-names-dropdown", "value")])
def reset_nclicks(tickers_list):
	return 0
"""
@app.callback([
	Output("market-cap","children"),
	Output("trailing-annual-dy","children"),
	Output("trailing-pe","children"),
	Output("forward-pe","children")],
	[Input("ticker-info","children"),])
def company_stats(ticker): 
	data = eval(ticker[1])

	if data["marketCap"]>1000000 and data["marketCap"]<1000000000:
		market_cap = round(data["marketCap"]/1000000,1)
		market_cap = "$"+str(market_cap)+"M"
	elif data["marketCap"]>1000000000 and data["marketCap"]<1000000000000:
		market_cap = round(data["marketCap"]/1000000000,1)
		market_cap = "$"+str(market_cap)+"B"



	print(data["marketCap"])
	company_ = html.Div([
		html.Div([html.H6(data["marketCap"]), html.P("Market Cap")],className="column mini_container"),
        html.Div([html.H6(data["trailingAnnualDividendYield"]), html.P("Dividend Yield")],className="column mini_container"),
        html.Div([html.H6(data["trailingPE"]), html.P("Price Earnings")],className="column mini_container"),
        html.Div([html.H6(data["forwardPE"]), html.P("forwardPE")],className="column mini_container"),
        ],className="row")

	keys1 = ("regularMarketOpen","regularMarketDayHigh","regularMarketDayLow","marketCap")
	keys2 = ("forwardPE","sharesOutstanding","fiftyTwoWeekHigh","fiftyTwoWeekLow")
	d1 = {k:data[k] for k in set(data).intersection(keys1)}
	d2 = {k:data[k] for k in set(data).intersection(keys2)}
	df1 = pd.DataFrame(list(d1.items()))
	df1.columns = ["key1", "value1"]
	df2 = pd.DataFrame(list(d2.items()))
	df2.columns = ["key2", "value2"]
	df_joint = pd.concat([df1,df2], axis=1)
	
	stats_table = html.Div([
		    html.Div([dt.DataTable(columns = [{"id":c ,"name":""} for c in df_joint.columns],
		        data=df_joint.to_dict("rows"),
		        style_cell={"minWidth":"75px", 
		        "textAlign":"left",
		        'boxShadow': "0 0",
		        "backgroundColor":"rgba(0,0,0,0)",
		        "border":"0px 0px 0px 0px"},
		        style_header={"border":"rgba(0,0,0,0)"},style_data={"border":"rgba(0,0,0,0)"})
		    ])
		    ])	    
	return html.P("maintainance")"""



@app.callback(Output("run-backtest", "n_clicks"), 
	[Input("selected-portfolio", "children")])
def reset_nclicks(tickers_list):
	return 0

@app.callback(
	Output("backtest-results", "children"),
	[Input("run-backtest", "n_clicks"),
	Input("selected-portfolio", "children")])
def backtest_results(n_clicks, tickers_list):
	if n_clicks == 1 and tickers_list is not None:
		portfolio = []
		for i in tickers_list["props"]["data"]:
			portfolio.append(i["ticker"])
		results = backtest_olmar(portfolio)
		returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results)
		round_trips = pf.round_trips.extract_round_trips(transactions.drop(["dt"], axis=1))
		round_trip_stats = pf.round_trips.gen_round_trip_stats(round_trips)
		data_sets = {
		                "returns":returns.to_json(orient='split', date_format='iso'),
		                "positions":positions.to_json(orient='split', date_format='iso'),
		                "transactions":transactions.to_json(orient='split', date_format='iso'),
		                "round_trip_stats":[round_trip_stats[key].to_json(orient='split', date_format='iso') for key in round_trip_stats.keys()]
		                }
		return json.dumps(data_sets)
	else:
		raise PreventUpdate
"""
@app.callback([
	 Output("boxplots", "children"),
	 Output("returns-heatmap", "children"),
	 Output("rolling-vol", "children"),
	 Output("rolling-sharpe", "children")],
	[Input("run-backtest", "n_clicks"),
	 Input("backtest-results", "children")])
def returns(n_clicks, backtest_results_df):
	if n_clicks == 0:
		raise PreventUpdate
	if n_clicks == 1:
	    data = json.loads(backtest_results_df)
	    returns = eval(data["returns"])
	    returns = pd.DataFrame(returns)
	    returns.index = pd.to_datetime(returns["index"])
	    returns = returns.drop(["index","name"], axis=1)

	    layout_figure = copy.deepcopy(layout)
        
        #monthly returns heatmap
	    monthly_ret_table = ep.aggregate_returns(returns["data"], 'monthly')
	    monthly_ret_table = monthly_ret_table.unstack().round(3)
	    returns_heatmap = go.Figure(data=go.Heatmap(z=100*monthly_ret_table.fillna(0).values, 
	    	x=monthly_ret_table.columns,
	    	y=monthly_ret_table.index, 
	    	colorscale='rdylgn'), layout=go_layout)
	    returns_heatmap = html.Div(dcc.Graph(id="returns-heatmap", 
	    	figure=returns_heatmap, 
	    	config={'displayModeBar':False}), className="pretty_container")
	    
	    #monthly returns distribution
	    returns_monthly_dist = go.Figure(
	    	data=[go.Histogram(x=100*monthly_ret_table.fillna(0).values)],
	    	layout=go_layout)
	    returns_monthly_dist_figure = dcc.Graph(id="returns-monthly-dist", 
	    	figure=returns_monthly_dist, 
	    	config={'displayModeBar':False})

	    ann_ret_df = pd.DataFrame(ep.aggregate_returns(returns["data"], 'yearly'))

	    #rolling volatility plot
	    rolling_vol = pf.timeseries.rolling_volatility(returns["data"], 30)
	    rolling_vol_figure =go.Figure(layout=go_layout)
	    rolling_vol_figure.add_trace(go.Scatter(
	    	x=returns.index,
	    	y=rolling_vol,
	    	line=dict(width=2.5, color='rgb(143, 7, 138)')))
	    rolling_vol_graph = dcc.Graph(id="rolling-vol",
	    	figure=rolling_vol_figure,
	    	config={'displayModeBar':False})

	    #rolling sharpe ratio
	    rolling_sharpe = pf.timeseries.rolling_sharpe(returns["data"], 30)
	    rolling_sharpe_figure = go.Figure(layout=go_layout)
	    rolling_sharpe_figure.add_trace(go.Scatter(
	    	x=returns.index,
	    	y=rolling_sharpe,
	    	line=dict(width=2.5, color='rgb(31, 3, 171)')))
	    rolling_sharpe_graph = dcc.Graph(id="rolling-sharpe",
	    	figure=rolling_sharpe_figure,
	    	config={'displayModeBar':False})

	    #returns boxplots
	    daily_box = returns["data"]
	    weekly_box = ep.aggregate_returns(returns["data"], "weekly")
	    monthly_box = ep.aggregate_returns(returns["data"], "monthly")
	    box_figure = go.Figure(layout=go_layout)
	    box_figure.add_trace(go.Box(y=daily_box, name="daily"))
	    box_figure.add_trace(go.Box(y=weekly_box, name="weekly"))
	    box_figure.add_trace(go.Box(y=monthly_box, name="monthly"))
	    boxplots_graph = dcc.Graph(id="boxplots",
	    	figure=box_figure,
	    	config={'displayModeBar':False})

	return [boxplots_graph,
	        returns_heatmap, 
	        rolling_vol_graph,
	        rolling_sharpe_graph]"""

@app.callback(
	Output("positions", "children"),
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def positions(n_clicks, backtest_results_df):
	if n_clicks == 0:
		raise PreventUpdate
	if n_clicks == 1:
	    data = json.loads(backtest_results_df)
	    #print(data["transactions"])
	    """print("returns")
	    print(returns)
	    positions = eval(data["positions"])
	    print("positions")
	    print(positions)
	    transactions = data["transactions"]
	    print("transactions")
	    print(transactions)"""

	    returns = eval(data["returns"])
	    returns_df = pd.DataFrame(returns["data"])
	    returns_df.index = pd.to_datetime(returns["index"])
	    positions = eval(data["positions"])
	    column_names = []
	    for i in range(0,len(positions["columns"])-1):
	        column_names.append(positions["columns"][i]["symbol"])
	    column_names.append(positions["columns"][-1])
	    positions_df = pd.DataFrame(positions["data"])
	    positions_df.columns = column_names
	    positions_df.index = pd.to_datetime(positions["index"])
	    positions_month = positions_df.resample('1M').mean()
	    layout_figure = copy.deepcopy(layout)
	    
	    positions_alloc_ = pf.pos.get_percent_alloc(positions_df)
	    positions_alloc = positions_alloc_.resample("M").mean()
	    top_ten = pf.pos.get_top_long_short_abs(positions_df)
	    position_concentration = pf.pos.get_max_median_position_concentration(positions_df)
	    long_short = pf.pos.get_long_short_pos(positions_df)
	    
	    symbol_sector_map = {}
	    sectors = []
	    for ticker in column_names[:-1]:
	    	sectors.append(stock_data.loc[ticker]["sector"])
	    	symbol_sector_map[ticker] = stock_data.loc[ticker]["sector"]
	    
	    holdings_figure = go.Figure(layout=go_layout)
	    holdings_figure.update_layout(title="Portfolio Holdings")
	    for ticker in column_names[:-1]:
	    	holdings_figure.add_trace(go.Scatter(x=positions_month.index, y=positions_month[ticker], mode='lines+markers', name=ticker))
	    holdings_graph = html.Div(dcc.Graph(id="positions",figure=holdings_figure,config={'displayModeBar':False}))

	    sector_exposure = pf.pos.get_sector_exposures(positions_df, symbol_sector_map)
	    sector_exposure_ = sector_exposure.resample("M").mean()
	    exposure_figure = go.Figure(layout=go_layout)
	    exposure_figure.update_layout(title="Portfolio Exposure By Sector")
	    for sector in set(sectors):
	    	exposure_figure.add_trace(go.Scatter(x=sector_exposure_.index, y=sector_exposure_[sector], mode='lines+markers',name=sector))
	    exposure_graph = html.Div(dcc.Graph(id="exposure",figure=exposure_figure,config={'displayModeBar':False}))

	    #for sector in symbol_sector_map
	    #exposure_graph = html.Div(dcc.Graph(id="exposure",figure=sector_exposure_figure,config={'displayModeBar':False}))

	    return html.Div([holdings_graph, exposure_graph])

#summary statistics
@app.callback([
	Output("returns-container","children"),
	Output("drawdown-container", "children")],
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def summary_stats(n_clicks, backtest_results_df):
	factor_returns = benchmark_df
	if n_clicks==0:
		raise PreventUpdate
	if n_clicks==1:
		data = json.loads(backtest_results_df)
		round_trip_pnl_stats = data["round_trip_stats"]
		round_trip_pnl=json.loads(round_trip_pnl_stats[0])
		round_trip_summary = json.loads(round_trip_pnl_stats[1])
		round_trip_returns = json.loads(round_trip_pnl_stats[2])
		round_trip_duration = json.loads(round_trip_pnl_stats[3])

		round_trip_pnl_df = pd.DataFrame(round_trip_pnl["data"], columns=round_trip_pnl["columns"])
		round_trip_pnl_df["names"] = round_trip_pnl["index"]

		round_trip_summary = pd.DataFrame(round_trip_pnl["data"], columns=round_trip_pnl["columns"])
		round_trip_summary["names"] = round_trip_pnl["index"]

		round_trip_returns = pd.DataFrame(round_trip_pnl["data"], columns=round_trip_pnl["columns"])
		round_trip_returns["names"] = round_trip_pnl["index"]

		round_trip_duration = pd.DataFrame(round_trip_pnl["data"], columns=round_trip_pnl["columns"])
		round_trip_duration["names"] = round_trip_pnl["index"]
		#print(round_trip_pnl_stats_df)
		#round_trip_pnl_df = pd.DataFrame(round_trip_pnl["data"], column_names=round_trip_pnl["columns"])
		#print(round_trip_pnl_df)
		returns_dict = eval(data["returns"])
		returns = pd.DataFrame(returns_dict["data"])
		returns.columns = ["returns"]
		returns.index = pd.to_datetime(returns_dict["index"])
		
		cum_returns_final = html.Div([
			html.H6(str(round(100*ep.cum_returns_final(returns["returns"]),2))+"%"
				, style={"font-weight":"bold","color":"white", "margin-bottom":"0px","margin-left":"10px"}),
			html.P("Returns",style={"font-weight":"400","color":"white","margin-top":"0px", "margin-left":"10px"})]
			, className="three columns", style={"background-color":"rgba(15,64,168)","border-radius":"5px"})

		cagr = html.Div([
			    html.H6(str(round(100*ep.cagr(returns["returns"]),2))+"%",
			    	style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			    html.P("Growth Rate",style={"font-weight":"400","color":"white","margin-top":"0px", "margin-left":"10px"})]
			, className="three columns", style={"background-color":"rgba(62,110,240)","border-radius":"5px"})

		alpha_, beta_ = ep.alpha_beta(returns["returns"], factor_returns)
		alpha = html.Div([
			    html.H6(round(alpha_,2),
			    	style={"font-weight":"bold","color":"white","margin-bottom":"0px", "margin-left":"10px"}),
			    html.P("Alpha",style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})] 
			, className="three columns", style={"background-color":"rgba(62,166,240)","border-radius":"5px"})
		annual_volatility = html.Div([
			    html.H6(str(round(100*ep.annual_volatility(returns["returns"]),2))+"%",
			    	style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			    html.P("Volatility",style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})] 
			, className="three columns", style={"background-color":"rgba(13,129,158)","border-radius":"5px"})
		
		returns_stats = html.Div([
			cum_returns_final,
			cagr,
			annual_volatility,
			alpha], className="row")
		#cummulative returns graph
		cum_returns_figure = go.Figure(layout=go_layout)
		cum_returns_figure.add_trace(go.Scatter(x=returns.index,y=ep.cum_returns(returns["returns"]),mode='lines',fill='tozeroy',line=dict(width=1.3, color='rgba(207, 25, 128)')))
		cum_returns_graph = html.Div(dcc.Graph(id="cum-returns",figure=cum_returns_figure,config={'displayModeBar':False}))
		returns_container = html.Div([html.Div(returns_stats),cum_returns_graph], className="pretty_container")

		#drawdown underwater
		max_dd = html.Div([
			        html.H6(str(round(100*ep.max_drawdown(returns["returns"]),2))+"%",
			            style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			        html.P("Max Drawdown", style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})]
			        , className="three columns",style={"background-color":"rgba(95, 13, 158)","border-radius":"5px"})

		value_at_risk = html.Div([
			                html.H6(str(round(100*ep.value_at_risk(returns["returns"]),2))+"%",
			                	style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			                html.P("Value at Risk", style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})]
			                    , className="three columns",style={"background-color":"rgba(110, 13, 158)","border-radius":"5px"})

		downside_risk = html.Div([
			                html.H6(str(round(100*ep.downside_risk(returns["returns"]),2))+"%",
			                	style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			                html.P("Down Risk", style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})]
			                    , className="three columns",style={"background-color":"rgba(144, 13, 158)","border-radius":"5px"})

		downside_risk = html.Div([
			                html.H6(str(round(100*ep.downside_risk(returns["returns"]),2))+"%",
			                	style={"font-weight":"bold","color":"white", "margin-bottom":"0px", "margin-left":"10px"}),
			                html.P("Down Risk", style={"font-weight":"400","color":"white","margin-top":"0px","margin-left":"10px"})]
			                    , className="three columns",style={"background-color":"rgba(158, 13, 112)","border-radius":"5px"})



		drawdown_stats = html.Div([max_dd,value_at_risk,downside_risk,downside_risk], className="row")
		df_cum_rets = ep.cum_returns(returns["returns"], starting_value=1.0)
		running_max = np.maximum.accumulate(df_cum_rets)
		underwater = -100*((running_max-df_cum_rets)/running_max)
		underwater_figure = go.Figure(layout=go_layout)
		underwater_figure.add_trace(go.Scatter(x=returns.index,y=underwater,mode='lines',fill='tozeroy',line=dict(width=1.3, color="red")))
		underwater_graph = html.Div(dcc.Graph(id="underwater", figure=underwater_figure, config={'displayModeBar':False}))
		drawdown_container = html.Div([html.Div(drawdown_stats),underwater_graph], className="pretty_container")
		
	return [returns_container, drawdown_container]
	    	
"""
@app.callback(
	Output("transactions", "children"),
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def transactions(n_clicks, backtest_results_df):
"""	

if __name__=="__main__":
    app.run_server(debug=True)
