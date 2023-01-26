import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import boto3
import s3fs

s3 = boto3.client('s3')
csw = pd.read_csv('s3://isfl-surrender-bot/procSW.csv')
curS = csw.S
curW = csw.W

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
# server = app.server

navItems = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Statistics",href='/playerlookup'),
                dbc.DropdownMenuItem("Resume",href='/playerresume'),
            ],
            menu_variant='dark',
            nav=True,
            in_navbar=True,
            label='Player Lookup',
            align_end=True,
        ),
        # dbc.NavItem(dbc.NavLink("Player Lookup", href="/playerlookup")),
            # className="g-0 ms-auto flex-nowrap mt-3 mt-md-0"),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Regular Season", header=True),
                dbc.DropdownMenuItem("Career Records", href="/career"),
                dbc.DropdownMenuItem("Season Records", href="/season"),
                dbc.DropdownMenuItem("Game Records", href="/game"),
                dbc.DropdownMenuItem("Postseason", header=True),
                dbc.DropdownMenuItem("Career Records", href="/careerpost"),
                dbc.DropdownMenuItem("Season Records", href="/seasonpost"),
                dbc.DropdownMenuItem("Game Records", href="/gamepost"),
            ],
            menu_variant="dark",
            nav=True,
            in_navbar=True,
            label="League Records",
            align_end=True,
            # className="g-0 ms-auto flex-nowrap mt-3 mt-md-0"
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Regular Season", header=True),
                dbc.DropdownMenuItem("Career Records", href="/teamcareer"),
                dbc.DropdownMenuItem("Season Records", href="/teamseason"),
                dbc.DropdownMenuItem("Postseason", header=True),
                dbc.DropdownMenuItem("Career Records", href="/teamcareerpost"),
                dbc.DropdownMenuItem("Season Records", href="/teamseasonpost"),
            ],
            menu_variant="dark",
            nav=True,
            in_navbar=True,
            label="Team Records",
            align_end=True,
            # className="g-0 ms-auto flex-nowrap mt-3 mt-md-0"
        ),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Buy a Treato", href="https://www.buymeacoffee.com/wolfiebot"),
                dbc.DropdownMenuItem("Discord Bot", href="https://discord.com/api/oauth2/authorize?client_id=802584570029146182&permissions=18432&scope=bot"),
            ],
            menu_variant="dark",
            nav=True,
            in_navbar=True,
            label="Other",
            align_end=True,
            # className="g-0 ms-auto flex-nowrap mt-3 mt-md-0"
        ),
    ]
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="assets/logo.png", height="30px")),
                        dbc.Col(dbc.NavbarBrand("WolfieBot Dashboards", className="ms-2 d-none d-sm-block")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.Row(
                [
                    dbc.NavbarToggler(id="navbar-toggler",className='ms-2'),
                    dbc.Collapse(
                        navItems,
                        id="navbar-collapse",
                        is_open=False,
                        className='ml-auto work-sans',
                        navbar=True,
                        # className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
                    ),
                ],
                
            )
        ], fluid=True, 
    ),
    color="dark",
    dark=True,
    className = 'w-100',
)

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

footer = dash.html.Footer(
    dbc.Container(
        [
            html.Hr(),
            html.Small(
                '''updated as of S%i W%i  |  made with <3 by infinitempg'''%(curS,curW))
        ]
    ), className = 'text-end fst-italic pe-2'
)


app.layout = html.Div([navbar,dash.page_container,footer],className='dbc')

if __name__ == "__main__":
    app.run(debug=False)