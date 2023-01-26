import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim
import pandas as pd
import boto3
import s3fs

dash.register_page(__name__, path='/', name='Home') # '/' is home page

s3 = boto3.client('s3')
csw = pd.read_csv('s3://isfl-surrender-bot/procSW.csv')
curS = csw.S
curW = csw.W

urlprefix="https://index.sim-football.com"
Sstr=str(curS.iloc[0])
conf2 = pd.read_html("%s/ISFLS%s/Index.html"%(urlprefix,Sstr),skiprows=1)[1].dropna()
conf1 = pd.read_html("%s/ISFLS%s/Index.html"%(urlprefix,Sstr),skiprows=1)[2].dropna()

conf1[['W','L','T','PF','PA']] = conf1[['W','L','T','PF','PA']].apply(pd.to_numeric,downcast='integer',errors='ignore')
conf1['Pct'] = conf1['Pct'].apply(pd.to_numeric,errors='ignore').round(decimals=4)
conf2[['W','L','T','PF','PA']] = conf2[['W','L','T','PF','PA']].apply(pd.to_numeric,downcast='integer',errors='ignore')
conf2['Pct'] = conf2['Pct'].apply(pd.to_numeric,errors='ignore').round(decimals=4)

layout = dbc.Container(
    [
        dbc.Alert("Updated as of S%i W%i."%(curS,curW), color="secondary", className='w-100'),
        dbc.Row(
            [
                dbc.Row(
                    [
                        html.H3("ASFC Standings"),
                        dash_table.DataTable(
                            data = conf2.to_dict('records'),
                            columns = [{"name": i, "id": i} for i in conf2.columns],
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'fontWeight':'bold',
                            },
                        ),
                        # dbc.Table.from_dataframe(conf2,striped=True,bordered=True,hover=True,responsive='m',color='dark'),
                    ], className='w-100',
                ),
                dbc.Row(
                    [
                        html.H3("NSFC Standings"),
                        dash_table.DataTable(
                            data = conf1.to_dict('records'),
                            columns = [{"name": i, "id": i} for i in conf1.columns],
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'fontWeight':'bold',
                            },
                        ),
                        # dbc.Table.from_dataframe(conf1,striped=True,bordered=True,hover=True,responsive='m',color='dark'),
                    ], className='w-100'
                ),
            ]
        ),
    ],
    # style={"padding-top":"10px",},
    className='dbc pt-2',
)