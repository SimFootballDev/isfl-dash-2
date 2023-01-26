import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import boto3
import s3fs
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim


dash.register_page(__name__, name='Season Records')

def formatter(value):
#     print(value)
    if any(item in value for item in ['Avg','Rat']):
        # print('rat')
        formatting = Format(precision=3,scheme=Scheme.fixed).group(True)
    elif 'Pct' in value:
        # print('Pct')
        formatting = Format(precision=3, scheme=Scheme.percentage).group(True)
    else:
        formatting = Format(precision=2, scheme=Scheme.decimal_integer).group(True)
        # print('decimal')
#     print(formatting)
    return formatting

s3 = boto3.client('s3')
csw = pd.read_csv('s3://isfl-surrender-bot/procSW.csv')
curS = csw.S
curW = csw.W

season = pd.read_csv('s3://isfl-surrender-bot/AllStats/season.csv')

dpdown0_s = [{"label": i, "value": (i)} for i in ['Passing','Rushing','Receiving','Kicking','Punting','Defense','Special Teams','All-Purpose','Offensive Line','Other']]

passValues = ['Pass Yds', 'Pass Avg', 'Pass TD', 'Pass Int', 'Pass Rat', 'Pass Cmp', 'Pass Att', 'Pass Pct']

dpdown_s = [{"label": i, "value": (i)} for i in passValues]

layout = dbc.Container([

    dcc.Markdown('''
        # ISFL Season Records

        Choose a statistic:
    ''', className='pt-2'),
    html.Div(dcc.Dropdown(id='dropdown0_s', options=dpdown0_s, value='Passing'),className="dbc w-50"),
    html.Div(dcc.Dropdown(id='dropdown_s', options=dpdown_s, value='Pass Yds'),className='dbc w-50'),
    html.Div(id='table-container_s',  className='tableDiv w-90'),
], className='dbc')

@callback(
    Output('dropdown_s','options'),
    Input('dropdown0_s','value')
)

def changeStats_s(value):
    if value == 'Passing':
        return [{'label': i, 'value': i} for i in ['Pass Yds', 'Pass Avg', 'Pass TD', 'Pass Int', 'Pass Rat', 'Pass Cmp', 'Pass Att', 'Pass Pct']]
    elif value == 'Rushing':
        return [{'label': i, 'value': i} for i in ['Rush Att', 'Rush Yds', 'Rush Avg', 'Rush TD']]
    elif value == 'Receiving':
        return [{'label': i, 'value': i} for i in ['Rec Rec', 'Rec Yds', 'Rec Avg', 'Rec TD']]
    elif value == 'Kicking':
        return [{'label': i, 'value': i} for i in ['K XPM', 'K XPA', 'K XPPct', 'K FGM', 'K FGA', 'K FGPct', 'K FG_U20 Pct', 'K FG_2029 Pct', 'K FG_3039 Pct', 'K FG_4049 Pct', 'K FG_50 Pct', 'K FGM_U20', 'K FGA_U20', 'K FGM_2029', 'K FGA_2029', 'K FGM_3039', 'K FGA_3039', 'K FGM_4049', 'K FGA_4049', 'K FGM_50', 'K FGA_50']]
    elif value == 'Punting':
        return [{'label': i, 'value': i} for i in ['P Punts', 'P Yds', 'P Avg', 'P Lng', 'P Inside 20','P In20Rate',]]
    elif value == 'Defense':
        return [{'label': i, 'value': i} for i in ['DEF Tck', 'DEF TFL', 'DEF Sack', 'DEF PD', 'DEF Int', 'DEF Sfty', 'DEF TD', 'DEF FF', 'DEF FR', 'DEF Blk P', 'DEF Blk XP', 'DEF Blk FG']]
    elif value == 'All-Purpose':
        return [{'label': i, 'value': i} for i in ['AllPurpose Yds', 'AllPurpose TD', 'Scrimmage Yds', 'Scrimmage TD', 'Points']]
    elif value == 'Special Teams':
        return [{'label': i, 'value': i} for i in ['ST KR', 'ST KRYds', 'ST PRYds', 'ST KRAvg', 'ST PRAvg', 'ST KR_TD', 'ST PR_TD', 'ST PR', 'ST KRLng', 'ST PRLng']]
    elif value == 'Offensive Line':
        return [{'label': i, 'value': i} for i in ['Other Pancakes', 'Other Sacks Allowed']]
    elif value == 'Other':
        return [{'label': i, 'value': i} for i in ['Other Penalties', 'Other Yards']]

@callback(
    Output('table-container_s','children'),
    Input('dropdown_s', 'value')
)

def display_table_s(value):
    prefix = value.split(' ')[0]
    if prefix == 'Pass':
        limit = ['Pass Att',25]
    elif prefix == 'Rush':
        limit = ['Rush Att',10]
    elif prefix == 'Rec':
        limit = ['Rec Rec',10]
    elif prefix == 'K':
        limit = ['K FGA',10]
    elif prefix == 'P':
        limit = ['P Punts',10]
    elif prefix == 'AllPurpose':
        limit = ['AllPurpose Yds', 1]
    elif prefix == 'Points':
        limit = ['Points', 1]
    elif prefix == 'Scrimmage':
        limit = ['Scrimmage Yds', 1]
    elif prefix == 'DEF':
        limit = ['DEF Tck', 1]
    elif prefix == 'ST':
        limit = ['ST KR', 0]
    elif prefix == 'Other':
        if prefix == "Other Penalties":
            limit = ['Other Penalties', 1]
        elif prefix == "Other Yards":
            limit = ['Other Penalties', 1]
        else:
            limit = ['Other Pancakes', 1]
            
    df_temp = season.loc[season[limit[0]] >= limit[1],['FullName', 'S',  value]].rename(columns={'FullName':'Player'})
    df_temp['Rank'] = df_temp[value].rank(method='min',ascending=False)
    df_temp = df_temp[['Rank', 'S', 'Player', value]].sort_values('Rank')
    return html.Div(
        [
            dcc.Markdown("Minimum %i %s."%(limit[1],limit[0]),className='pt-2'),
            dash_table.DataTable(
                id='main-table_s',
                columns = [
                    dict(id='Rank',name='Rank',type='numeric'),
                    dict(id='S',name='S',type='numeric'),
                    dict(id='Player',name='Player',type='text'),
                    dict(id=value,name=value,type='numeric',format=formatter(value))
                ],
                data=df_temp.to_dict('records'),
                sort_action='native',
                filter_action="native",
                page_current=0,
                page_size=10,
                page_action='native',
                style_cell_conditional=[
                    {'if': {'column_id': 'Rank'},
                    'max-width': '100px'},
                    {'if': {'column_id': 'S'},
                    'max-width': '100px'},
                ],
                style_header={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'fontWeight':'bold',
                },
            )
        ],
    )