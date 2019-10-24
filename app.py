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
from collections import OrderedDict
import pytz
from olmar import backtest_olmar
import pyfolio as pf
import json
import empyrical as ep
import dash_bootstrap_components as dbc
import yfinance as yf

stock_data = pd.read_csv(os.path.join(os.getcwd(),'data/new_stock_data.csv'))
stock_data.index = stock_data["symbol"]
dropdown_options = [{'label':stock_data['name'][i], 'value':stock_data['symbol'][i]} for i in range(0,len(stock_data))]
stock_data.index = stock_data["symbol"]
stock_data.drop("symbol", axis=1)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',dbc.themes.BOOTSTRAP]

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
	external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', ])

server = app.server
app.layout = html.Div([
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
		            html.Div([
		                html.Div([
		                    html.Div([
		                        html.Div([
		        	                html.H5(id="name", style={"color":"black"}),
		        	                html.H6(id="sector-industry", style={"marging-top":"0rem"})], className="ten columns"),
		        	            html.Div(html.Button('+ portfolio',id='add-ticker-but',n_clicks=0), style={"float":"right"}, 
		        		            className="two columns dcc_control")], 
		        	        style={"marging-top":"25px"} ,className="row"),
		                    ])
		                ]),

                    dcc.Tabs(id="tabs",mobile_breakpoint=0, value="overview", parent_className="custom-tabs",
        	            children=[
                            dcc.Tab(label="Overview", value="overview", 
                	            children=[
                		            html.Div([html.Div(id="previous-close")]),
                		            html.Div([
		        	                    dcc.Tabs(id="time-tabs", mobile_breakpoint=0, value="1-month-tab",parent_className="custom-tabs",
		        		                    children=[
		        		                        dcc.Tab(label="1 month", value="1-month-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="6 months", value="6-months-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="1 year", value="1-year-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected"),
		        		                        dcc.Tab(label="5 years", value="5-years-tab", className="custom-tab", 
		        		          	                selected_className="custom-tab--selected")]
		        		                    , colors={"border":"rgba(0,0,0,0)","background":"rgba(0,0,0,0)"}),            
		                                    html.Div(id="price-history-figure", style={"marging-bottom":"25px"})
		                                ]),
                
		                            html.Div(id="company-stats")], className="custom-tab", selected_className="custom-tab--selected"),

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
                	    	children=[
                	    	    html.Div(id="annual-return"),
                	    	    html.Div(id="annual-volatility"),
                	    	    html.Div(id="calmar-ratio"),
                	    	    html.Div(id="omega-ratio"),
                	    	    html.Div(id="sharpe-ratio"),
                	    	    html.Div(id="sortino-ratio"),
                	    	    html.Div(id="downside-risk"),
                	    	    html.Div(id="stability"),
                	    	    html.Div(id="tail-ratio"),
                	    	    html.Div(id="cagr")], className="custom-tab"),
                	    dcc.Tab(label="RETURNS", value="returns", selected_className="custom-tab--selected",
                		    children=[
                		        html.Div([
		                            html.Div([html.Div(id="cum-returns")]),
		                            html.Div([html.Div(id="underwater")]),
		                            html.Div([
		            	                html.Div([
		    	                            html.Div(id="boxplots", className="five columns"),
		    	                            html.Div(id="returns-heatmap", className="seven columns")], className="row flex-display")]),
		                            html.Div([html.Div(id="rolling-vol")]),
		                            html.Div([html.Div(id="rolling-sharpe")])])], className="custom-tab"),
                	    dcc.Tab(label="POSITIONS", value="positions", selected_className="custom-tab--selected",
                		    children=[], className="custom-tab"),
                	    dcc.Tab(label="TRANSACTIONS", value="transactions", selected_className="custom-tab--selected",
                		    children=[], className="custom-tab"),
                	]),
                html.Div([html.Button('run backtest', id='run-backtest',n_clicks=0, style={"float":"right"})],
		             className="dcc_control", style = {"marging-bottom":"0px"}),
		    
	            html.Div(id="backtest-results", style={"display":"none"})], 
	        className="custom-tab", selected_className="custom-tab--selected")
	    ])######end tabs here                                               #3
    ]),
	
	#returns,
            
    #positions
    html.Div([
        html.Div([
            html.Div(id="holdings")])])
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
		rmc_tag = html.H6("+"+str(rmc)+"("+str(np.abs(rmcp))+"%"+")"+"\U00002191", style={"margim-bottom":"0px","color":"green"})
	else:
		rmc_tag = html.H6("-"+str(rmc)+"("+str(np.abs(rmcp))+"%"+")"+"\U00002193", style={"margim-bottom":"0px","color":"red"})
	
	return html.Div([
		html.Div([html.H5(str(ticker_stats['regularMarketPreviousClose'])+" USD")],style={"color":"black"}, className="column"),
		html.Div([rmc_tag], className="column")], className="row")


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

@app.callback(Output("company-stats", "children"),
	[Input("ticker-info","children")])
def company_stats(ticker): 
	data = eval(ticker[1])
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
	return stats_table


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
		data_sets = {
		                "returns":returns.to_json(orient='split', date_format='iso'),
		                "positions":positions.to_json(orient='split', date_format='iso'),
		                "transactions":transactions.to_json(orient='split', date_format='iso')
		                }
		return json.dumps(data_sets)
	else:
		raise PreventUpdate

@app.callback(
	[Output("cum-returns", "children"),
	 Output("underwater", "children"),
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
	    
	    #cummulative returns graph
	    cum_returns_figure = go.Figure(layout=go_layout)
	    cum_returns_figure.add_trace(go.Scatter(
	    	x=returns.index,
	    	y=np.cumprod(1+returns["data"])-1,
	    	mode='lines',
	    	fill='tozeroy',
	    	line=dict(width=1.3, color='green'))) 
	    cum_returns_graph = dcc.Graph(id="cum-returns", 
	    	figure=cum_returns_figure, 
	    	config={'displayModeBar':False})
        
        #monthly returns heatmap
	    monthly_ret_table = ep.aggregate_returns(returns["data"], 'monthly')
	    monthly_ret_table = monthly_ret_table.unstack().round(3)
	    returns_heatmap = go.Figure(data=go.Heatmap(z=100*monthly_ret_table.fillna(0).values, 
	    	x=monthly_ret_table.columns,
	    	y=monthly_ret_table.index, 
	    	colorscale='rdylgn'), layout=go_layout)
	    returns_heatmap = dcc.Graph(id="returns-heatmap", 
	    	figure=returns_heatmap, 
	    	config={'displayModeBar':False})
	    
	    #monthly returns distribution
	    """returns_monthly_dist = go.Figure(
	    	data=[go.Histogram(x=100*monthly_ret_table.fillna(0).values)],
	    	layout=go_layout)
	    returns_monthly_dist_figure = dcc.Graph(id="returns-monthly-dist", 
	    	figure=returns_monthly_dist, 
	    	config={'displayModeBar':False})"""

	    #drawdown underwater 
	    df_cum_rets = ep.cum_returns(returns["data"], starting_value=1.0)
	    running_max = np.maximum.accumulate(df_cum_rets)
	    underwater = -100*((running_max-df_cum_rets)/running_max)
	    underwater_figure = go.Figure(layout=go_layout)
	    underwater_figure.add_trace(go.Scatter(
	    	x=returns.index,
	    	y=underwater,
	    	mode='lines',
	    	fill='tozeroy',
	    	line=dict(width=1.3, color='red')))
	    
	    underwater_graph = dcc.Graph(id="underwater", 
	    	figure=underwater_figure, 
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

	return [cum_returns_graph, 
	        underwater_graph, 
	        boxplots_graph,
	        returns_heatmap, 
	        rolling_vol_graph,
	        rolling_sharpe_graph] 

@app.callback(
	Output("holdings", "children"),
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def positions(n_clicks, backtest_results_df):
	if n_clicks == 0:
		raise PreventUpdate
	if n_clicks == 1:
	    data = json.loads(backtest_results_df)

	    positions = eval(data["positions"])
	    column_names = []
	    for i in range(0,len(positions["columns"])-1):
	        column_names.append(positions["columns"][i]["symbol"])
	    column_names.append(positions["columns"][-1])
	    positions_df = pd.DataFrame(positions["data"])
	    positions_df.columns = column_names
	    positions_df.index = pd.to_datetime(positions["index"])
	    positions_month = positions_df.resample('1M')
	    layout_figure = copy.deepcopy(layout)

#summary statistics
@app.callback([Output("annual-return","children"),
	Output("cagr","children"),
	Output("annual-volatility","children"),
	Output("calmar-ratio","children"),
	Output("omega-ratio","children"),
	Output("sharpe-ratio","children"),
	Output("sortino-ratio","children"),
	Output("downside-risk","children"),
	Output("stability","children"),
	Output("tail-ratio","children")],
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def summary_stats(n_clicks, backtest_results_df):
	if n_clicks==0:
		raise PreventUpdate
	if n_clicks==1:
		data = json.loads(backtest_results_df)
		returns_dict = eval(data["returns"])
		returns = pd.DataFrame(returns_dict["data"])
		returns.columns = ["returns"]
		returns.index = pd.to_datetime(returns_dict["index"])
		
		annual_return = ep.annual_return(returns)
		annual_volatility = ep.annual_volatility(returns)
		calmar_ratio = ep.calmar_ratio(returns["returns"])
		omega_ratio = ep.omega_ratio(returns["returns"])
		sharpe_ratio = ep.sharpe_ratio(returns["returns"])
		sortino_ratio = ep.sortino_ratio(returns["returns"])
		downside_risk = ep.downside_risk(returns["returns"])
		#information_ratio = ep.information_ratio(returns["returns"])
		#alpha_beta = ep.alpha_beta(returns["returns"])
		#alpha = ep.alpha(returns["returns"])
		#beta = ep.beta(rreturns["returns"])
		stability = ep.stability_of_timeseries(returns["returns"])
		tail_ratio = ep.tail_ratio(returns["returns"])
		cagr = ep.cagr(returns["returns"])
	return [annual_return, 
		    cagr,
		    annual_volatility,
		    calmar_ratio,
            omega_ratio,
            sharpe_ratio,
		    sortino_ratio,
		    downside_risk,
		    stability,
		    tail_ratio]


	    	
"""
@app.callback(
	Output("transactions", "children"),
	[Input("run-backtest", "n_clicks"),
	Input("backtest-results", "children")])
def transactions(n_clicks, backtest_results_df):
	pass"""

if __name__=="__main__":
    app.run_server(debug=True)
