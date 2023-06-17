import dash
from dash import dcc
from dash import html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import ta
# model
from model import prediction
from sklearn.svm import SVR


def get_stock_price_fig(df):

    fig = go.Figure(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    ))
    fig.update_layout(
    title='Trading Chart View',
    yaxis_title='Price',
    xaxis_title='Date',
)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def get_more(df):
    df['MA_12'] = df['Close'].rolling(window=12).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="MA_12",
                     title="Moving Average vs Date")
    fig.update_traces(mode='lines')
    return fig

def get_moree(df):
    df['MA_21'] = df['Close'].rolling(window=21).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="MA_21",
                     title="Moving Average vs Date")
    fig.update_traces(mode='lines')
    return fig

def get_moreee(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    fig = px.scatter(df,
                     x="Date",
                     y="RSI",
                     title="Relative Strength Index")
    fig.update_traces(mode='lines')
    return fig


app = dash.Dash( __name__ )
server = app.server
# html layout of site
app.layout = html.Div(
    [
        html.Div(
            [
                # Navigation
                html.P("Visualising and forecasting stocks using Dash", className="start"),
                html.Div([
                    html.P("Input stock code: "),
                    html.Div([
                        dcc.Input(id="dropdown_tickers", type="text"),
                        html.Button("Submit", id='submit'),
                    ],
                             className="form")
                ],
                         className="input-place"),
                html.Div([
                    dcc.DatePickerRange(id='my-date-picker-range',
                                        min_date_allowed=dt(1999, 12, 12),
                                        max_date_allowed=dt.now(),
                                        initial_visible_month=dt.now(),
                                        end_date=dt.now().date()),
                ],
                         className="date"),
                html.Div([
                    html.Button(
                        "Stock Price", className="stock-btn", id="stock"),
                    html.Button("Moving Avg 12",
                                className="indicators-btn",
                                id="indicators"),
                    html.Button("RSI",
                                className="indicators-btn",
                                id="indicatorsss"),
                    html.Button("Moving Avg 21",
                                className="indicators-btn",
                                id="indicatorss"),
                    
                    dcc.Input(id="n_days",
                              type="text",
                              placeholder="number of days"),
                    html.Button(
                       "Forecast", className="forecast-btn", id="forecast")
                ],
                         className="buttons"),
            ],
            className="nav"),

        # content
        html.Div(
            [
                     html.Div(
                    [  # header
                        html.Img(id="logo"),
                        html.P(id="ticker")
                    ],
                    className="header"),

                html.Div(id="description"),
                html.Div([], id="graphs-content"),
                html.Div([], id="main-content"),
                html.Div([], id="main-content1"),
                html.Div([], id="main-content2"),
                html.Div([], id="forecast-content")
            ],
            className="content"),
    ],
    className="container")


# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
], [
    Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        #return [['Hi there! Please enter a valid stock ticker to get details.']]
        return "Hi there! Please enter a valid stock ticker to get details.","https://a.c-dn.net/b/1c4R4K/headline_GettyImages-1062952818.jpg","Stock Analysis"
        # raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            symbol = inf.get("longName")
            #logo_url = inf.info["logo"]
            long=inf.get("region")
            quote=inf.get("quoteType")
            state=inf.get("marketState")
            if symbol is None:
                return [["No information found for {}".format(val)]]
            else:
               # return [["Stock Name :{}".format(symbol),"region : {}".format(long)]]
              return "Stock Name --- {} <><><> Region --- {} <><><> Quote --- {} <><><> Market State --- {} ".format(symbol, long, quote,state),None,None

# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]



# callback for indicators
@app.callback([Output("main-content1", "children")], [
    Input("indicatorss", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_moree(df_more)
    return [dcc.Graph(figure=fig)]

# callback for indicators
@app.callback([Output("main-content2", "children")], [
    Input("indicatorsss", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_moreee(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
