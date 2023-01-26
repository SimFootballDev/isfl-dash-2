import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim
import pandas as pd
import boto3
import s3fs

dash.register_page(__name__, path='/playerresume', name='Player Resume') # '/' is home page

s3 = boto3.client('s3')
csw = pd.read_csv('s3://isfl-surrender-bot/procSW.csv')
curS = csw.S[0]
curW = csw.W[0]

career = pd.read_csv('s3://isfl-surrender-bot/AllStats/career.csv').set_index('FullName')
pcareer = pd.read_csv('s3://isfl-surrender-bot/AllStats/pcareer.csv').set_index('FullName')
season = pd.read_csv('s3://isfl-surrender-bot/AllStats/season.csv').set_index(['S','FullName'])
pseason = pd.read_csv('s3://isfl-surrender-bot/AllStats/pseason.csv').set_index(['S','FullName'])
game = pd.read_csv('s3://isfl-surrender-bot/AllStats/game.csv',low_memory=False).set_index(['S','W','FullName'])
pgame = pd.read_csv('s3://isfl-surrender-bot/AllStats/pgame.csv').set_index(['S','W','FullName'])

careerRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/career.csv').set_index('FullName')
pcareerRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/pcareer.csv').set_index('FullName')
seasonRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/season.csv').set_index(['S','FullName'])
pseasonRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/pseason.csv').set_index(['S','FullName'])
gameRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/game.csv').set_index(['S','W','FullName'])
pgameRank = pd.read_csv('s3://isfl-surrender-bot/AllStats/Ranks/pgame.csv').set_index(['S','W','FullName'])

allAwardsDF = pd.read_csv('s3://isfl-surrender-bot/allAwards.csv').set_index('S').fillna('')

probowls = {}
allpros = {}
allpros2 = {}

for k in range(1,curS):
    try:
        probowls[k] = pd.read_csv('s3://isfl-surrender-bot/ProBowls/S%02dProBowl.csv'%k,index_col='Position',names=['Position','S%i'%k]).iloc[:,0]
    except:
        pass
    try:
        allpros[k] = pd.read_csv('s3://isfl-surrender-bot/AllPros/S%02dAllProFirst.csv'%k,index_col='Position',names=['Position','S%i'%k]).iloc[:,0]
        allpros2[k] = pd.read_csv('s3://isfl-surrender-bot/AllPros/S%02dAllProSecond.csv'%k,index_col='Position',names=['Position','S%i'%k]).iloc[:,0]
    except:
        pass

ultimus = pd.read_csv('s3://isfl-surrender-bot/ultimus.csv').set_index('S')

optionsPlayers = [{"label":career.sort_index().index.tolist()[i], "value":career.sort_index().index.tolist()[i]} for i in range(0,len(career))]

layout = dbc.Container([
    dcc.Markdown(
        [
            '''
            # Player Resume Lookup

            Player:
            '''
        ],
        className='pt-2'
    ),
    dcc.Dropdown(id='my-input2', options=optionsPlayers, value='', placeholder='Type a player name.', className='dbc w-100'),
    html.Hr(),
    html.Div(id='my-output2'),
    ], className='dbc'
)

@callback(
    Output(component_id='my-output2', component_property='children'),
    Input(component_id='my-input2', component_property='value')
)

def update_output_div(player):
    
    if player == '':
        return ''

    activeSeasons = season.xs(player,level=1).index
    playerNames = game.loc[game.PlayerID == game.xs(player,level=2).PlayerID.unique()[0]].reset_index().FullName.unique()
    teams = pd.concat(game.xs(p,level=2).reset_index().groupby(['S','W','Team'])[['S','W','Team']].tail(1).set_index('S') for p in playerNames)

    teamList = []
    for t in teams.Team.unique():
        minS = teams.loc[teams.Team == t].iloc[0].name
        maxS = teams.loc[teams.Team == t].iloc[-1].name
        teamList.append("%s (S%i - S%i)"%(t, minS, maxS))
    teamsU = pd.concat(game.xs(p,level=2).reset_index().groupby(['S'])[['S','Team']].tail(1).set_index('S') for p in playerNames)
    ultimusList = []
    for t in teamsU.index:
        try:
            if teamsU.at[t,'Team'] == ultimus.at[t,'Team']:
                ultimusList.append('S%i'%(t))
        except KeyError:
            continue
    if len(ultimusList) == 0: 
        ultimusDisplay = 'none'
    else: 
        ultimusDisplay = 'block'

    awardsList = []
    playerAwardDF = pd.DataFrame()
    for i,seasonAwards in allAwardsDF.iterrows():
        for awardidx, winners in enumerate(seasonAwards):
            if player in winners:
                award = pd.DataFrame([i,seasonAwards.index[awardidx]]).T
                playerAwardDF = pd.concat([playerAwardDF,award])
    playerAwardDF = playerAwardDF.rename(columns={0:'S',1:'Award'})    
    if len(playerAwardDF) > 0:
        for a in allAwardsDF.columns:
            if a not in playerAwardDF.Award.unique():
                continue
            aDF = playerAwardDF.loc[playerAwardDF.Award == a]
            num = len(aDF)
            seasons = ", ".join(['S%i'%s for s in aDF.S])
            awardsList.append("\t%ix %s (%s)"%(num,a,seasons))
    
    probowllist = []
    allprolist = []
    allpro2list = []
    for i in activeSeasons:
        probowlAS = probowls.get(i)
        allproAS = allpros.get(i)
        allpro2AS = allpros2.get(i)

        try:
            probowlapp = len(pd.concat(probowlAS[probowlAS.str.contains(p)] for p in playerNames))
            if probowlapp > 0:
                probowllist.append("S%i"%i)
        except:
            continue

        try:
            allproapp = len(pd.concat(allproAS[allproAS.str.contains(p)] for p in playerNames))
            if allproapp > 0:
                allprolist.append("S%i"%i)
        except:
            continue


        try:
            allpro2app = len(pd.concat(allpro2AS[allpro2AS.str.contains(p)] for p in playerNames))
            if allpro2app > 0:
                allpro2list.append("S%i"%i)
        except:
            continue
            
    if len(probowllist) > 0:
        awardsList.append("\t%ix Pro Bowler (%s)"%(len(probowllist),', '.join(probowllist)))
            
    if len(allprolist) > 0:
        awardsList.append("\t%ix First Team All-Pro (%s)"%(len(allprolist),', '.join(allprolist)))
            
    if len(allpro2list) > 0:
        awardsList.append("\t%ix Second Team All-Pro (%s)"%(len(allpro2list),', '.join(allpro2list)))

    if len(awardsList) == 0:
        awardsDisplay = 'none'
    else:
        awardsDisplay = 'block'

    careerList = []
    careplayerTable = pd.concat([careerRank.loc[player,tableStats].rename('Rank'),career.loc[player,tableStats].rename('Total')],axis=1)
    carplayerTable20 = careplayerTable.loc[(careplayerTable.Rank <= 20) & (careplayerTable.Total > 0)]
    for s in range(0,len(carplayerTable20)):
        careerList.append("\t#%i Career %s (%.2f)"%(carplayerTable20.iloc[s,0],carplayerTable20.index[s],carplayerTable20.iloc[s,1]))
    
    if len(careerList) == 0:
        careerDisplay = 'none'
    else:
        careerDisplay = 'block'

    seasonList = []
    spRanks = seasonRank.loc[:,tableStats].xs(player,level=1)
    spTotals = season.loc[:,tableStats].xs(player,level=1)
    for stat in spRanks.T.index:
        splayerTable = pd.concat([spRanks.T.loc[stat].rename('Rank'),spTotals.T.loc[stat].rename('Total')],axis=1)
        splayerTable20 = splayerTable.loc[(splayerTable.Rank <= 20) & (splayerTable.Total > 0)].sort_values('Rank')
        for s in range(0,len(splayerTable20)):
            seasonList.append("\t#%i Season %s (S%i - %.2f)"%(splayerTable20.iloc[s,0],stat,splayerTable20.index[s],splayerTable20.iloc[s,1]))
     
    if len(seasonList) == 0:
        seasonDisplay = 'none'
    else:
        seasonDisplay = 'block'
        
    gameList = []
    gpRanks = gameRank.loc[:,tableStats].xs(player,level=2)
    gpTotals = game.loc[:,tableStats].xs(player,level=2)
    for stat in gpRanks.T.index:
        if stat == 'K XPPct' or stat == 'K FGPct':
            continue
        gplayerTable = pd.concat([gpRanks.T.loc[stat].rename('Rank'),gpTotals.T.loc[stat].rename('Total')],axis=1)
        gplayerTable20 = gplayerTable.loc[(gplayerTable.Rank <= 20) & (gplayerTable.Total > 0)].sort_values('Rank')
        for s in range(0,len(gplayerTable20)):
            gameList.append("\t#%i Game %s (S%iW%i - %.2f)"%(gplayerTable20.iloc[s,0],stat,gplayerTable20.index[s][0],gplayerTable20.index[s][1],gplayerTable20.iloc[s,1]))
        
    if len(gameList) == 0:
        gameDisplay = 'none'
    else:
        gameDisplay = 'block'
    

    pcarList = []
    try:
        pcplayerTable = pd.concat([pcareerRank.loc[player,tableStats].rename('Rank'),pcareer.loc[player,tableStats].rename('Total')],axis=1)
        pcplayerTable20 = pcplayerTable.loc[(pcplayerTable.Rank <= 20) & (pcplayerTable.Total > 0)]
        for s in range(0,len(pcplayerTable20)):
            pcarList.append("\t#%i Career %s (%.2f)"%(pcplayerTable20.iloc[s,0],pcplayerTable20.index[s],pcplayerTable20.iloc[s,1]))
        if len(pcarList) == 0:
            pcDisplay = 'none'
        else:
            pcDisplay = 'block'
    except:
        # postDisplay = 'none'
        pcDisplay = 'none'

    
    pseasList = []
    try:
        pspRanks = pseasonRank.loc[:,tableStats].xs(player,level=1)
        pspTotals = pseason.loc[:,tableStats].xs(player,level=1)
        for stat in pspRanks.T.index:
            psplayerTable = pd.concat([pspRanks.T.loc[stat].rename('Rank'),pspTotals.T.loc[stat].rename('Total')],axis=1)
            psplayerTable20 = psplayerTable.loc[(psplayerTable.Rank <= 20) & (psplayerTable.Total > 0)].sort_values('Rank')
            for s in range(0,len(psplayerTable20)):
                pseasList.append("\t#%i Season %s (S%i - %.2f)"%(psplayerTable20.iloc[s,0],stat,psplayerTable20.index[s],psplayerTable20.iloc[s,1]))
        if len(pseasList) == 0:
            psDisplay = 'none'
        else:
            psDisplay = 'block'
    except:
        psDisplay = 'none'
    
    pgameList = []
    try:
        pgpRanks = pgameRank.loc[:,tableStats].xs(player,level=2)
        pgpTotals = pgame.loc[:,tableStats].xs(player,level=2)
        for stat in pgpRanks.T.index:
            if stat == 'K XPPct' or stat == 'K FGPct':
                continue
            pgplayerTable = pd.concat([pgpRanks.T.loc[stat].rename('Rank'),pgpTotals.T.loc[stat].rename('Total')],axis=1)
            pgplayerTable20 = pgplayerTable.loc[(pgplayerTable.Rank <= 20) & (pgplayerTable.Total > 0)].sort_values('Rank')
            for s in range(0,len(pgplayerTable20)):
                pgameList.append("\t#%i Game %s (S%iW%i - %.2f)"%(pgplayerTable20.iloc[s,0],stat,pgplayerTable20.index[s][0],pgplayerTable20.index[s][1],pgplayerTable20.iloc[s,1]))
        if len(pgameList) == 0:
            pgDisplay = 'none'
        else:
            pgDisplay = 'block'

    except KeyError:
        # print('')
        # postDisplay = 'none'
        pgDisplay = 'none'

    return dbc.Container(
        [
            dcc.Markdown("## %s"%player),
            html.Div([dcc.Markdown("###### %s"%t) for t in teamList]),
            html.Div(html.P("%ix Ultimus Champion (%s)"%(len(ultimusList),', '.join(ultimusList))),style={'display':ultimusDisplay}),

            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in awardsList],
                        title="Awards",
                        style={'display':awardsDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in careerList],
                        title="Career Records",
                        style={'display':careerDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in seasonList],
                        title="Season Records",
                        style={'display':seasonDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in gameList],
                        title="Game Records",
                        style={'display':gameDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in pcarList],
                        title="Postseason Career Records",
                        style={'display':pcDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in pseasList],
                        title="Postseason Season Records",
                        style={'display':psDisplay},
                        class_name='border',
                    ),
                    dbc.AccordionItem(
                        children = [dcc.Markdown("%s"%a) for a in pgameList],
                        title="Postseason Game Records",
                        style={'display':pgDisplay},
                        class_name='border',
                    ),
                ],
                always_open=True,
                start_collapsed = True,
            ),
        ],
    )

tableStats = ['Pass Yds', 'Pass Avg', 'Pass TD',
       'Pass Int', 'Pass Rat', 'Pass Cmp', 'Pass Att', 'Rush Att', 'Rush Yds',
       'Rush Avg', 'Rush Lg', 'Rush TD', 'Rec Rec', 'Rec Yds', 'Rec Avg',
       'Rec Lg', 'Rec TD', 'K XPM', 'K XPA', 'P Punts', 'P Yds', 'P Avg',
       'P Lng', 'P Inside 20', 'DEF Tck', 'DEF TFL', 'DEF Sack', 'DEF PD',
       'DEF Int', 'DEF Sfty', 'DEF TD', 'DEF FF', 'DEF FR', 'DEF Blk P',
       'DEF Blk XP', 'DEF Blk FG', 'ST KR', 'ST KRYds', 'ST PRYds', 'ST KRLng',
       'ST PRLng', 'ST KR_TD', 'ST PR_TD', 'ST PR', 'Other Pancakes', 'Other Sacks Allowed',
       'Pass Pct', 'P In20Rate', 'ST KRAvg', 'ST PRAvg', 'K XPPct', 'K FGM',
       'K FGA', 'K FGPct', 'AllPurpose Yds', 'Scrimmage Yds', 'Points']

passStats = ['Pass Yds', 'Pass Avg', 'Pass TD', 'Pass Int', 'Pass Rat', 'Pass Cmp', 'Pass Att', 'Pass Pct']
rushStats = ['Rush Att', 'Rush Yds', 'Rush Avg', 'Rush TD']
recStats = ['Rec Rec', 'Rec Yds', 'Rec Avg', 'Rec TD']
kickStats = ['K XPM', 'K XPA', 'K XPPct', 'K FGM', 'K FGA', 'K FGPct', 'K FG_U20 Pct', 'K FG_2029 Pct', 'K FG_3039 Pct', 'K FG_4049 Pct', 'K FG_50 Pct']
puntStats = ['P Punts', 'P Yds', 'P Avg', 'P Lng', 'P Inside 20','P In20Rate',]
defStats = ['DEF Tck', 'DEF TFL', 'DEF Sack', 'DEF PD', 'DEF Int', 'DEF Sfty', 'DEF TD', 'DEF FF', 'DEF FR', 'DEF Blk P', 'DEF Blk XP', 'DEF Blk FG']
allStats = ['AllPurpose Yds', 'AllPurpose TD', 'Scrimmage Yds', 'Scrimmage TD', 'Points']
stStats = ['ST KR', 'ST KRYds', 'ST PRYds', 'ST KRAvg', 'ST PRAvg', 'ST KR_TD', 'ST PR_TD', 'ST PR', 'ST KRLng', 'ST PRLng']
olStats = ['Other Pancakes', 'Other Sacks Allowed']
otherStats = ['Other Penalties', 'Other Yards']