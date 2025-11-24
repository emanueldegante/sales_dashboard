# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 00:39:50 2025

@author: emanu
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# -------------------- USER AUTH --------------------
VALID_USERNAME_PASSWORD_PAIRS = {
"Hugo": "TruXegexl48",
"Jordan": "c5jahIqIh1m",
"Hartley": "spiPhuwRaC3"
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# -------------------- LOAD DATA --------------------
df = pd.read_csv("22_SLIPS_DB_Batch_Final_Nov_24.csv")
df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], errors="coerce")

# -------------------- LAYOUT WITH LOGIN --------------------
app.layout = dbc.Container([

    # ---------------- LOGIN SECTION ----------------
    html.Div(id="login-section", children=[
        dbc.Row([
            dbc.Col(html.H2("DTScope Login", style={'color':'white','textAlign':'center'})),
        ], justify='center'),
        dbc.Row([
            dbc.Col(dcc.Input(id="username", type="text", placeholder="Username", style={'width':'100%'}), width=6),
        ], justify='center', className="mb-2"),
        dbc.Row([
            dbc.Col(dcc.Input(id="password", type="password", placeholder="Password", style={'width':'100%'}), width=6),
        ], justify='center', className="mb-2"),
        dbc.Row([
            dbc.Col(html.Button("Login", id="login-btn", n_clicks=0, style={
                'backgroundColor':'blue','color':'white','fontSize':'16px','fontWeight':'bold',
                'borderRadius':'8px','border':'none','padding':'10px 20px','width':'100%','cursor':'pointer'
            }), width=6),
        ], justify='center'),
        html.Div(id="login-message", style={'color':'red','textAlign':'center','marginTop':'10px'})
    ], style={'marginTop':'50px'}),

    # ---------------- DASHBOARD CONTENT ----------------
    html.Div(id="dashboard-content", style={"display":"none"}, children=[

        # FIXED IMAGES
        html.Div([
            html.Img(src="/assets/lady_jane.PNG", style={"position":"fixed","top":"10px","left":"10px","width":"120px","zIndex":"9999"}),
            html.Img(src="/assets/sauce.PNG", style={"position":"fixed","top":"10px","right":"10px","width":"120px","zIndex":"9999"})
        ]),

        html.H2("Lady Jane - Sales Dashboard", className="mt-5 mb-4 text-center"),

        # FILTERS
        dbc.Row([
            dbc.Col([
                html.Label("Client"),
                dcc.Dropdown(
                    id="client-filter",
                    options=[{"label": c, "value": c} for c in sorted(df["Client"].dropna().unique())],
                    multi=True, placeholder="Select Client(s)"
                )
            ], width=3),
            dbc.Col([
                html.Label("Product"),
                dcc.Dropdown(
                    id="product-filter",
                    options=[{"label": p, "value": p} for p in sorted(df["Product"].dropna().unique())],
                    multi=True, placeholder="Select Product(s)"
                )
            ], width=3),
            dbc.Col([
                html.Label("LOT"),
                dcc.Dropdown(
                    id="lot-filter",
                    options=[{"label": l, "value": l} for l in sorted(df["LOT"].dropna().unique())],
                    multi=True, placeholder="Select LOT(s)"
                )
            ], width=3),
            dbc.Col([
                html.Label("Ship Date Range"),
                dcc.DatePickerRange(
                    id="ship-date-range",
                    min_date_allowed=df["Ship_Date"].min(),
                    max_date_allowed=df["Ship_Date"].max(),
                    start_date=df["Ship_Date"].min(),
                    end_date=df["Ship_Date"].max()
                )
            ], width=3),
        ], className="mb-4"),

        # CHARTS ROW 1
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Total Units by Client"),
                dbc.CardBody([dcc.Graph(id="client-pie")])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Product Mix (R/G) by Client"),
                dbc.CardBody([dcc.Graph(id="product-mix")])
            ]), width=8)
        ]),

        html.Br(),

        # CHARTS ROW 2
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Total Units by Month (Shipping Month)"),
                dbc.CardBody([dcc.Graph(id="monthly-trend")])
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Selected LOT Details"),
                dbc.CardBody([dcc.Graph(id="lot-table")])
            ]), width=6),
        ])

    ])
])

# -------------------- LOGIN CALLBACK --------------------
@app.callback(
    Output("login-section", "style"),
    Output("dashboard-content", "style"),
    Output("login-message", "children"),
    Input("login-btn", "n_clicks"),
    State("username", "value"),
    State("password", "value")
)
def login(n_clicks, username, password):
    if n_clicks > 0:
        if username in VALID_USERNAME_PASSWORD_PAIRS and VALID_USERNAME_PASSWORD_PAIRS[username] == password:
            return {"display": "none"}, {"display": "block"}, ""
        else:
            return {"display": "block"}, {"display": "none"}, "Invalid username or password"
    return {"display": "block"}, {"display": "none"}, ""

# -------------------- DASHBOARD CALLBACK --------------------
@app.callback(
    [
        Output("client-pie", "figure"),
        Output("product-mix", "figure"),
        Output("monthly-trend", "figure"),
        Output("lot-table", "figure"),
    ],
    [
        Input("client-filter", "value"),
        Input("product-filter", "value"),
        Input("lot-filter", "value"),
        Input("ship-date-range", "start_date"),
        Input("ship-date-range", "end_date"),
    ]
)
def update_dashboard(selected_clients, selected_products, selected_lots, start_date, end_date):
    dff = df.copy()

    # Filters
    if selected_clients:
        dff = dff[dff["Client"].isin(selected_clients)]
    if selected_products:
        dff = dff[dff["Product"].isin(selected_products)]
    if selected_lots:
        dff = dff[dff["LOT"].isin(selected_lots)]

    # Default date range
    if not start_date:
        start_date = df["Ship_Date"].min()
    if not end_date:
        end_date = df["Ship_Date"].max()
    dff = dff[(dff["Ship_Date"] >= start_date) & (dff["Ship_Date"] <= end_date)]

    # Pie Chart
    if dff.empty:
        pie_fig = px.pie(title="No Data")
    else:
        cqty = dff.groupby("Client")["QTY (#Units)"].sum().reset_index()
        pie_fig = px.pie(cqty, names="Client", values="QTY (#Units)")
        pie_fig.update_traces(textposition='inside', textinfo='percent+label')

    # Product Mix
    if dff.empty:
        mix_fig = px.bar(title="No Data")
    else:
        mix = dff.groupby(["Client", "Product"])["QTY (#Units)"].sum().reset_index()
        mix_fig = px.bar(mix, x="Client", y="QTY (#Units)", color="Product", barmode="stack")

    # Monthly Trend
    if dff.empty:
        monthly_fig = px.line(title="No Data")
    else:
        dff["Month"] = dff["Ship_Date"].dt.to_period("M").astype(str)
        monthly = dff.groupby("Month")["QTY (#Units)"].sum().reset_index().sort_values("Month")
        monthly_fig = px.line(monthly, x="Month", y="QTY (#Units)", markers=True)

    # LOT Details
    if dff.empty:
        lot_fig = px.bar(title="No Data")
    else:
        lotdata = dff[["LOT", "Client", "Product", "QTY (#Units)", "Ship_Date"]]
        lot_fig = px.bar(lotdata, x="Ship_Date", y="QTY (#Units)", color="LOT", hover_data=["Client", "Product"])

    return pie_fig, mix_fig, monthly_fig, lot_fig

# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)  # Render automatically assigns ports
