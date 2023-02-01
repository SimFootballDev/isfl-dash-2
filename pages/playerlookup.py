import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim
import pandas as pd
import boto3
import s3fs

dash.register_page(__name__, path='/playerlookup', name='Player Lookup') # '/' is home page

def formatter(value):
#     print(value)
    if any(item in value for item in ['Avg','Rat',]):
        # print('rat')
        formatting = Format(precision=3,scheme=Scheme.fixed).group(True)
    elif 'Pct' in value:
        # print('Pct')
        formatting = Format(precision=3, scheme=Scheme.percentage).group(True)
    elif 'Rate' in value:
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

career = pd.read_csv('s3://isfl-surrender-bot/AllStats/career.csv')
careerRanks = pd.read_csv("s3://isfl-surrender-bot/AllStats/Ranks/career.csv")
season = pd.read_csv('s3://isfl-surrender-bot/AllStats/season.csv').set_index('S').fillna(0)
game = pd.read_csv('s3://isfl-surrender-bot/AllStats/game.csv',low_memory=False)

optionsPlayers = [{"label":career.sort_values('FullName').iloc[i]['FullName'], "value":career.sort_values('FullName').iloc[i]['PlayerID']} for i in range(0,len(career))]

layout = dbc.Container([
    dcc.Markdown(
        [
            '''
            # Player Statistical Lookup

            Player:
            '''
        ],
        className='pt-2'
    ),
    dcc.Dropdown(id='my-input', options=optionsPlayers, value='', placeholder='Type a player name.', className='dbc w-100'),
    # html.H1("Player Statistical Lookup - Season by Season"),
    # html.P("Player ranks for efficiency statistics such as FG Pct may be off as players who did not reach the threshold are still counted."),
    # html.Div([
    #     "Player: ",
    #     dcc.Dropdown(id='my-input', options=optionsPlayers, value='', placeholder='Type a player name.', className='dbc w-50')
    # ]),
    html.Br(),
    html.Div(id='my-output'),
    ], className='dbc'
)

@callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)

def update_output_div(input_value):
    
    if input_value == '':
        return ''
    
    # sampleID = career.loc[career.FullName == input_value,'PlayerID'].iloc[0]
    playerCareer = career.loc[career.PlayerID == input_value].copy()
    playerCareer['Team'] = 'Career'
    playerRanks = careerRanks.loc[careerRanks.PlayerID == input_value].copy().fillna('DNQ').apply(pd.to_numeric,errors='ignore',downcast='integer').astype(str)
    playerRanks['Team'] = 'Rank'
    playerTeams = game.loc[game.PlayerID == input_value].groupby(['S','Team']).sum(numeric_only=True)
    playerSeasons = season.loc[season.PlayerID == input_value].copy()
    teamSeason = pd.DataFrame(['/'.join(list(playerTeams.reset_index().set_index('S').loc[l,'Team'])) if playerTeams.reset_index().set_index('S').index.value_counts().loc[l] > 1 else playerTeams.reset_index().set_index('S').loc[l,'Team'] for l in list(playerSeasons.index)],columns=['Team'],index=playerSeasons.index)
    df_temp = pd.concat([pd.concat([teamSeason,playerSeasons],axis=1).reset_index(names=['S']),playerCareer,playerRanks]).fillna('')
    
       
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in passStats]):
        passVis = 'none'
    else:
        passVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in rushStats]):
        rushVis = 'none'
    else:
        rushVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in recStats]):
        recVis = 'none'
    else:
        recVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in kickStats]):
        kickVis = 'none'
    else:
        kickVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in puntStats]):
        puntVis = 'none'
    else:
        puntVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in olStats]):
        olVis = 'none'
    else:
        olVis = 'block'
    
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in allStats]):
        allVis = 'none'
    else:
        allVis = 'block'
        
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in stStats]):
        stVis = 'none'
    else:
        stVis = 'block'
    
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in otherStats]):
        otherVis = 'none'
    else:
        otherVis = 'block'
    
    if all([((playerSeasons[o] == 0).all()) | (playerSeasons[o].isnull().all()) for o in defStats]):
        defVis = 'none'
    else:
        defVis = 'block'
        
    
    # cStat['S'] = ''
    # cStat['Team'] = 'Career'
    # df_temp = df_temp.append(cStat, ignore_index=True)
    # pcRank = pcRank.apply(pd.to_numeric,errors='ignore',downcast='integer').astype(str)
    # pcRank['S'] = ''
    # pcRank['Team'] = 'Rank'
    # # df_temp = pd.concat([df_temp,pcRank],axis=1)
    # df_temp = df_temp.append(pcRank, ignore_index=True)
    
    return dbc.Container([
        html.H3('Passing Statistics'),
        html.P('Ranks for a minimum of 50 Pass Att.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in passStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        ),
    ],style = {'display':passVis},),dbc.Container([
        html.H3('Rushing Statistics'),
        html.P('Ranks for a minimum of 25 Rush Att.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in rushStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],

            ),
            # className='dbc',
        )
    ],style = {'display':rushVis},),dbc.Container([
        html.H3('Receiving Statistics'),
        html.P('Ranks for a minimum of 50 Rec.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in recStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':recVis},), dbc.Container([
        html.H3('Defensive Statistics'),
        html.P('Ranks for a minimum of 1 DEF Tck.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in defStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':defVis},),dbc.Container([
        html.H3('Offensive Line Statistics'),
        html.P('Ranks for a minimum of 1 Pancake.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in olStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':olVis},),dbc.Container([
        html.H3('Kicking Statistics'),
        html.P('Ranks for a minimum of 25 FGA.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in kickStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':kickVis},),dbc.Container([
        html.H3('Punting Statistics'),
        html.P('Ranks for a minimum of 25 Punts.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in puntStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':puntVis},),dbc.Container([
        html.H3('Special Teams Statistics'),
        html.P('Ranks for a minimum of 1 KR/PR.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in stStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':stVis},),dbc.Container([
        html.H3('All-Purpose Statistics'),
        html.P('Ranks for a minimum of 1 AllPurpose Yd.'),
        html.P(dash_table.DataTable(
            id='main-table',
            columns = [
                dict(id='S',name='S',type='numeric'),
                dict(id='Team',name='Team',type='text'),
            ] + [dict(id=i,name=i,type='numeric',format=formatter(i)) for i in allStats],
            data=df_temp.to_dict('records'),
            sort_action='native',
            page_current=0,
            page_size=15,
            page_action='native',
            export_format='csv',
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight':'bold',
            },
            style_data_conditional=[
                {
                    "if": {"row_index": len(df_temp) - 2},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(50, 50, 50)',
                },
                {
                    "if": {"row_index": len(df_temp) - 1},
                    "fontWeight": "bold",
                    'backgroundColor': 'rgb(40, 40, 40)',
                },
            ],
            ),
            # className='dbc',
        )
    ],style = {'display':allVis},)

passStats = ['Pass Yds', 'Pass Avg', 'Pass TD', 'Pass Int', 'Pass Rat', 'Pass Cmp', 'Pass Att', 'Pass Pct']
rushStats = ['Rush Att', 'Rush Yds', 'Rush Avg', 'Rush TD','Rush Lg']
recStats = ['Rec Rec', 'Rec Yds', 'Rec Avg', 'Rec TD', 'Rec Lg']
kickStats = ['K XPM', 'K XPA', 'K XPPct', 'K FGM', 'K FGA', 'K FGPct', 'K FG_U20 Pct', 'K FG_2029 Pct', 'K FG_3039 Pct', 'K FG_4049 Pct', 'K FG_50 Pct']
puntStats = ['P Punts', 'P Yds', 'P Avg', 'P Lng', 'P Inside 20','P In20Rate',]
defStats = ['DEF Tck', 'DEF TFL', 'DEF Sack', 'DEF PD', 'DEF Int', 'DEF Sfty', 'DEF TD', 'DEF FF', 'DEF FR', 'DEF Blk P', 'DEF Blk XP', 'DEF Blk FG']
allStats = ['AllPurpose Yds', 'AllPurpose TD', 'Scrimmage Yds', 'Scrimmage TD', 'Points']
stStats = ['ST KR', 'ST KRYds', 'ST PRYds', 'ST KRAvg', 'ST PRAvg', 'ST KR_TD', 'ST PR_TD', 'ST PR', 'ST KRLng', 'ST PRLng']
olStats = ['Other Pancakes', 'Other Sacks Allowed']
otherStats = ['Other Penalties', 'Other Yards']