import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from sklearn import preprocessing
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly import tools



######################################################Data##############################################################

#path = 'https://raw.githubusercontent.com/MartaFaria/DV_Project_Migration/master/'

df = pd.read_excel('Migration_In_Out.xlsx')
df_ind = pd.read_excel('Migration_Indicators.xlsx')



###################################################Data Pre-processing###################################################
sum_mig = df.groupby(['Country', 'Year']).sum().reset_index() #reset_index is used to keep the original columns Country and Year

x = sum_mig[['Inflow', 'Outflow', 'Net-Migration']].values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df_scaled = pd.DataFrame(x_scaled)

sum_mig = pd.concat([sum_mig, df_scaled], axis=1)
sum_mig = sum_mig.rename(columns={0:'norm Inflow', 1:'norm Outflow', 2:'norm Net'})


df_avg = df_ind.groupby('Year').mean().reset_index()


######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df_ind['Country'].unique()]

mig_options = [
    {'label': 'Net-Migration', 'value': 'norm Net'},
    {'label': 'Migration Inflow', 'value': 'norm Inflow'},
    {'label': 'Migration Outflow', 'value': 'norm Outflow'}
]

year_options =[dict(label=Year, value=Year) for Year in df_ind['Year'].unique()]

dropdown_country = dcc.Dropdown(
    id='country_drop',
    options=[{'label': i, 'value': i} for i in df_ind['Country'].unique()
             ],
    value='Afghanistan',
    clearable=False
)



##################################################APP###############################################################

app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([

    html.Div([
        html.H1(
            'GLOBAL MIGRATION PATTERNS',
            style={'width': '100%', 'display': 'inline-block', 'height': '50px', 'font-family':'sans-serif',
                   'color':'#155724', 'text-align': 'center','vertical-align': 'top', 'padding': '0px'},
        ),

        html.H2(
            "An Overview",
            style={'width': '100%', 'display': 'inline-block', 'position': 'relative','height': '5px',
                   'color' : '#155724', 'font-family':'sans-serif', 'text-align': 'center','vertical-align': 'top', 'padding': '0px'}
        ),
    ]),

    html.Div([],style = {'width': '100%','backgroundColor':'#f2f2f2','padding':15, 'margin-bottom':0}),

    html.Div([
        html.Div([dcc.Markdown('### MIGRATION AROUND THE WORLD'
                               '\n\nMigration refers to the movement of people from place to place. People migrate for many different reasons, which can be classified as *economic*, *social*, *political* or *environmental*.'
                               '\n\n* **Economic migration** is related to finding work or better economic opportunities. '
                               '\n\n* **Social migration** refers to the search of a better quality of life or to be closer to family and friends.'
                               '\n\n* **Political migration** occurs when people is moving to escape conflict, political persecution, terrorism, or human rights violations. '
                               '\n\n* **Environmental** causes of migration include the adverse effects of climate change, natural disasters, and other environmental factors. '
                               '\n\nOver the last years, migration has become a key issue for countries all over the world. More people than ever live in a country other than the one in which they were born.' 
                               '\n\nTherefore, as a group, we thought that it would be interesting to explore migration patterns and their underlying causes.')
                  ], style={'width': '40%', 'text-align': 'justify', 'font-family':'sans-serif', 'font-size':'15px',
                            'position': 'relative', 'color': '#111', 'background-color':'#fffff'},
                 className='box'),

        html.Div([
            html.Div([dcc.RadioItems(id='mig_radio',
                                     options=mig_options,
                                     value='norm Net',
                                     labelStyle={'display': 'inline'})
                      ], style={'width': '100%', 'color': '#111', 'background-color': '#fffff', 'border-radius': '5px',
                                'text-align':'center', 'font-family':'sans-serif'}
                     ),

            html.Div([dcc.Graph(id='choropleth_graph')
                      ], style={'width': '100%','color': '#111', 'background-color': '#fffff', 'border-radius': '5px',
                                'font-family':'sans-serif','vertical-align': 'middle'}
                     ),

        ], style = {'width': '60%'},
        className='box')
    ], style = {'display': 'flex'}),

    html.Div([

        html.Div([
            html.Div([
                html.Label('Select country'),
                dropdown_country],
                style={'width': '100%', 'text-align': 'justify', 'horizontal-align': 'left', 'vertical-align': 'middle',
                       'margin-left': '10%', 'margin-right': '20%', 'font-family':'sans-serif', 'font-size':14, 'color':'#111'}),

            html.Br(),
            html.Br(),

            html.Div([
                html.Label('Select year'),
                dcc.Slider(
                    id='year_slider',
                    min=2008,
                    max=2017,
                    marks={i: '{}'.format(i) for i in range(2008, 2017)},
                    value=2017,
                    step=1,
                    included=False
                )], style={'width': '100%', 'text-align': 'justify', 'font-family':'sans-serif', 'font-size': 14,
                           'vertical-align': 'middle', 'horizontal-align': 'left', 'margin-left': '10%', 'margin-right': '10%',
                           'color':'#111'}),
        ], style={'width': '40%'}),

        html.Div([
            html.Div([
                html.Div([html.Div([html.H4("The selected country and year are:")],
                                   style={"font-size": 15, 'font-family':'sans-serif', 'horizontal-align': 'middle', 'color': '#111'}),
                          dcc.Loading(html.Div([html.H4("...")], id="box-country",
                                               style={"font-size": 19, 'font-family':'sans-serif', 'color': '#155724',
                                                      "font-weight": "bold", 'horizontal-align': 'middle'}))],
                         ),
            ], style={'margin-right': '5%', 'width': '100%', 'text-align': 'center', 'backgroundColor': '#fff',
                      'vertical-align': 'center', 'horizontal-align': 'middle', 'font-family':'sans-serif'}),

            html.Div([
                html.Div([html.Div([html.H4("Total number of migrants entering the country (Inflow)")],
                                   style={"font-size": 15, 'font-family':'sans-serif', 'horizontal-align': 'middle', 'color': '#111'}),
                          dcc.Loading(html.Div([html.H4("")], id="box-inflow",
                                               style={"font-size": 19, "font-weight": "bold",'vertical-align': 'middle', 'color': '#155724',
                                                      'horizontal-align': 'middle', 'font-family':'sans-serif',}))],
                         ),
            ], style={'margin-right': '5%', 'width': '100%', 'text-align': 'center', 'backgroundColor': '#fff',
                      'vertical-align': 'middle', 'horizontal-align': 'middle', 'font-family':'sans-serif',}),

            html.Div([
                html.Div([html.Div([html.H4("Total number of migrants leaving the country (Outflow)")],
                                   style={"font-size": 15, 'font-family':'sans-serif', 'horizontal-align': 'middle', 'color': '#111'}),
                          dcc.Loading(html.Div([html.H4("")], id="box-outflow",
                                               style={"font-size": 19, "font-weight": "bold", 'color': '#155724','font-family':'sans-serif',
                                                      'vertical-align': 'middle', 'horizontal-align': 'middle'}))]
                         ),
            ], style={'margin-right': '5%', 'width': '100%', 'text-align': 'center', 'backgroundColor': '#fff',
                      'vertical-align': 'middle', 'horizontal-align': 'middle'}),

            html.Div([
                html.Div([html.Div([html.H4("")], style={"font-size": 15, 'font-family':'sans-serif', 'horizontal-align': 'middle', 'color': '#111'}),
                          dcc.Loading(html.Div([html.H4("")], id="box-net",
                                               style={'width': '100%', 'font-family':'sans-serif', "font-size": 15,
                                                      "font-weight": "bold",'color': '#111'}))]
                         ),
            ], style={'margin-right': '5%', 'width': '100%', 'text-align': 'center', 'backgroundColor': '#fff',
                      'vertical-align': 'center', 'horizontal-align': 'middle'}),


        ], style={'display': 'flex', 'width': '60%', 'text-align': 'center', 'vertical-align': 'middle',
                  'margin-left': '10%', 'backgroundColor': '#fff'}),
    ], style={'display': 'flex', 'margin-left': '2%', 'margin-right': '2%',
              'margin': '10px', 'padding': '15px', 'position': 'relative','font-family': 'sans-serif'}, className='box'),

    html.Div([
        html.Br(),
        html.Div([dcc.Graph(id='hbar2')], style={'flex': '33%'}),
        html.Div([dcc.Graph(id='hbar1')], style={'flex': '33%'}),
        html.Div([dcc.Graph(id='line')], style={'flex': '33%'})
    ],
        style={'display': 'flex', 'color': '#111','font-family': 'sans-serif'},
        className='box'
    ),

    html.Div([
        html.Br(),
        html.Div([dcc.Graph(id='bar1')], style={'flex': '35%'}),
        html.Div([dcc.Graph(id='bar2')], style={'flex': '35%'}),
        html.Div([dcc.Graph(id='bar3')], style={'flex': '35%'}),
        html.Div([dcc.Graph(id='bar4')], style={'flex': '35%'})
    ],
        style={'display':'flex','color': '#111', 'font-family': 'sans-serif'},
        className='box'
    ),

    html.Div([
        html.Footer([
            html.Label(["Data Visualization | June 2020 | Carlos Pereira, M20190426 |"
                        " Cátia Duro, M20190394 | João Miguel Lopes, M20190465 | Marta Faria, M20190178"]),

            html.Label([" | Data available at: ",
                        html.A("OECD",
                               href="https://www.oecd.org/migration/mig/oecdmigrationdatabases.htm", target="_blank"),
                        ", ",
                        html.A("The Global Economy",
                               href="https://www.theglobaleconomy.com/", target="_blank"),
                        " and ",
                        html.A("Our World in Data",
                               href="https://ourworldindata.org/charts", target="_blank"),
                        ])],
                       style ={'width': '100%', 'display': 'inline-block', 'color' : '#111', 'font-family':'sans-serif',
                               'font-size':'12px', 'text-align': 'center','vertical-align': 'middle', 'font-weight':'bold',
                               'padding': '5px'}
       )])],className = 'body', style = {'backgroundColor':'#f2f2f2','padding':15, 'margin-bottom':0})


######################################################Callbacks#########################################################

#------------------------------------------------- Text boxs -----------------------------------------------------------

@app.callback(
    Output('box-country', 'children'),
    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
])
def update_box_country(countries, selected_year):
    box_country = countries + ', ' + str(selected_year)
    return box_country


@app.callback(
    Output('box-inflow', 'children'),
    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
])
def update_box_inflow(countries, year):
    df_year = df.loc[df['Year'] == year]
    df_year_country = df_year.loc[df_year['Country'] == countries]
    df_year_country_in = df_year_country['Inflow'].sum()
    box_inflow = str(df_year_country_in)
    return box_inflow


@app.callback(
    Output('box-outflow', 'children'),
    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
])
def update_box_outflow(countries, year):
    df_year = df.loc[df['Year'] == year]
    df_year_country = df_year.loc[df_year['Country'] == countries]
    df_year_country_out = df_year_country['Outflow'].sum()
    box_outflow = str(df_year_country_out)
    return box_outflow


@app.callback(
    Output('box-net', 'children'),
    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
])

def update_box_net(countries, year):
    df_year = df.loc[df['Year'] == year]
    df_year_country = df_year.loc[df_year['Country'] == countries]
    df_year_country_net = df_year_country['Net-Migration'].sum()
    if df_year_country_net>0:
        mig = 'entering'
    else:
        mig = 'leaving'
    box_net = 'In ' + str(year) + ', the migration flows in ' + countries + ' were mainly from people ' + mig + ' the country.'
    return box_net




#------------------------------------------------------ Choropleth Map --------------------------------------------------
@app.callback(
    Output('choropleth_graph', 'figure'),

    [Input('mig_radio', 'value')
     ]
)

def update_graph(migvar):
    if migvar=='norm Net':
        new_migvar='Net-Migration'
        hover_var = 'Net-Migration'
    elif migvar=='norm Inflow':
        new_migvar='Migrants Inflow'
        hover_var='Inflow'
    else:
        new_migvar='Migrants Outflow'
        hover_var='Outflow'


    data_choropleth = px.choropleth(sum_mig,
                                    locations="Country",
                                    locationmode="country names",
                                    color=migvar,
                                    hover_name="Country",
                                    hover_data=["Year", hover_var],
                                    color_continuous_scale='YlGn',
                                    animation_frame="Year",
                                    projection="natural earth",
                                    title=dict(text="<b>Global " + str(new_migvar) + '</b>', x=.5, font={"size": 20, 'family':'sans-serif',
                                                                                             'color':'#111'}),
                                    labels={migvar:'Number of migrants <br>(min-max normalization)',
                                                "size": 12, 'family':'sans-serif','color':'#111'})

    fig_choro = go.Figure(data=data_choropleth)

    return fig_choro

#--------------------------------------------------- Bar charts ----------------------------------------------------------
@app.callback(
    [Output('hbar1', 'figure'),
     Output('hbar2', 'figure')
     ],

    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
     ]
)

def update_graph(countries, year):
    df_year = df.loc[df['Year'] == year]


    df_year_country = df_year.loc[df_year['Country'] == countries]
    df_year_country_in = df_year_country.loc[df_year_country['Inflow']>0]
    top_ten_in = df_year_country_in.sort_values(by=['Inflow'], ascending=False)
    top_ten_in = top_ten_in.head(10)

    df_year_country_out = df_year_country.loc[df_year_country['Outflow'] > 0]
    top_ten_out = df_year_country_out.sort_values(by=['Outflow'], ascending=False)
    top_ten_out = top_ten_out.head(10)

    max_in = top_ten_in['Inflow'].max()
    max_out = top_ten_out['Outflow'].max()
    max_in_out = max(max_in, max_out)
    max_in_out = max_in_out + 500

    trace = go.Bar(
        x=top_ten_in["Inflow"],
        y=top_ten_in["Country of origin"],
        orientation="h",
        marker=dict(
            color='rgb(35,132,67)',
            line=dict(
                color='rgb(35,132,67)',
                width=10)
        ),
        width=.05
    )

    data_hbar = [trace]

    layout_hbar = dict(title=dict(text="Migration inflow - Top-10 countries<br>" + str(countries) + ", " + str(year),
                                  x=.5, font={"size": 15, 'family':'sans-serif', 'color':'#111'}),
                       xaxis=dict(title=dict(text="Number of migrants", font={"size": 13, 'family':'sans-serif', 'color':'#111'}),
                                  gridcolor="LightGrey",
                                  showline=True,
                                  range=[0, max_in_out],
                                  linecolor="rgb(89, 89, 89)",
                                  tickfont=dict(family="sans-serif", size=12, color='#111')),
                       yaxis=dict(tickfont=dict(family="sans-serif", size=12, color='#111'),
                                  autorange="reversed"),
                       paper_bgcolor="rgb(0,0,0,0)",
                       plot_bgcolor="rgb(0,0,0,0)",
                       )

    trace1 = go.Bar(
        x=top_ten_out["Outflow"],
        y=top_ten_out["Country of origin"],
        orientation="h",
        marker=dict(
            color='rgb(203,24,29)',
            line=dict(
                color='rgb(203,24,29)',
                width=10)
        ),
        width=.05
    )

    data_hbar1 = [trace1]

    layout_hbar1 = dict(title=dict(text="Migration outflow - Top-10 countries<br>"
                                        + str(countries) + ", " + str(year), x=.5, font={"size": 15, 'family':'sans-serif', 'color':'#111'}),
                        xaxis=dict(title=dict(text="Number of migrants", font={"size": 13, 'family':'sans-serif', 'color':'#111'}),
                                   gridcolor="LightGrey",
                                   showline=True,
                                   linecolor="rgb(89, 89, 89)",
                                   range=[max_in_out, 0],
                                   tickfont=dict(family="sans-serif", size=12, color='#111')),
                        yaxis=dict(tickfont=dict(family="sans-serif", size=12, color='#111'),
                                   autorange="reversed"),
                        paper_bgcolor="rgb(0,0,0,0)",
                        plot_bgcolor="rgb(0,0,0,0)"
                        )

    fig_bar = go.Figure(data=data_hbar, layout=layout_hbar)
    fig_bar1 = go.Figure(data=data_hbar1, layout=layout_hbar1)

    return fig_bar, fig_bar1




#--------------------------------------------------- Bar charts ----------------------------------------------------------
@app.callback(
    [Output('bar1', 'figure'),
     Output('bar2', 'figure'),
     Output('bar3', 'figure'),
     Output('bar4', 'figure'),
     Output('line', 'figure')
     ],

    [Input('country_drop', 'value'),
     Input('year_slider', 'value')
     ]
)

def update_graph(countries, year):
    year_aux = year-3
    if (year_aux<2010 and year<=2010):
        year_aux=2008
        year = 2010

    dff = df_ind[(df_ind['Year'] >= year_aux) & (df_ind['Year'] <= year)]
    dff_avg = df_avg[(df_avg['Year'] >= year_aux) & (df_avg['Year'] <= year)]

    df_bar = dff.loc[(dff['Country'] == countries)]

    max_in = df_bar['Inflow'].max()
    max_out = df_bar['Outflow'].max()
    max_in_out = max(max_in, max_out)
    max_in_out = max_in_out + 100


    data_bar = [
        go.Bar(
            x=df_bar['Year'],
            y=df_bar['Deaths - Conflict and terrorism'],
            orientation="v",
            showlegend=False,
            marker=dict(
                color='rgb(239,225,156)',
                line=dict(
                    color='rgb(217,240,163)',
                    width=12)
            ),
            width=.05
        ),
        go.Scatter(
            x=dff_avg['Year'],
            y=dff_avg['Deaths - Conflict and terrorism'],
            showlegend=False,
            mode='lines',
            line=dict(color="#000000", width=2)
    )]

    layout_bar = dict(title=dict(text="Deaths due to <br>conflicts and terrorism",
                                 x=.5, font={"size": 15, 'family':'sans-serif', 'color': '#111'}),
                      xaxis=dict(showline=True,
                                 linecolor="rgb(89, 89, 89)",
                                 tickmode='linear',
                                 tickangle=-90,
                                 tickfont=dict(family="sans-serif", size=12, color='#111')),
                      yaxis=dict(title=dict(text="Number of deaths per 100000 inhab", font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                 gridcolor="LightGrey",
                                 range=[0, 765],
                                 tickfont=dict(family="sans-serif", size=12, color='#111')
                                 ),
                      paper_bgcolor="#ffffff",
                      plot_bgcolor="#ffffff",
                      barmode='stack'
                      )

    data_bar2 = [go.Bar(
        x=df_bar['Year'],
        y=df_bar['GDP per capita'],
        orientation="v",
        showlegend=False,
        marker=dict(
            color='rgb(239,225,156)',
            line=dict(
                color='rgb(217,240,163)',
                width=12)
        ),
        width=.05
    ),
        go.Scatter(
            x=dff_avg['Year'],
            y=dff_avg['GDP per capita'],
            showlegend=False,
            mode='lines',
            line=dict(color="#000000", width=2)
        )
    ]

    layout_bar2 = dict(title=dict(text="GDP per capita",
                                  x=.5, font={"size": 15, 'family':'sans-serif', 'color': '#111'}),
                       xaxis=dict(showline=True,
                                  linecolor="rgb(89, 89, 89)",
                                  tickmode='linear',
                                  tickangle=-90,
                                  tickfont=dict(family="sans-serif", size=12, color='#111')),
                       yaxis=dict(title=dict(text="US Dollars", font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                  gridcolor="LightGrey",
                                  range=[0, 130000],
                                  tickfont=dict(family="sans-serif", size=12, color='#111')
                                  ),
                       paper_bgcolor="#ffffff",
                       plot_bgcolor="#ffffff",
                       barmode='stack'
                       )

    data_bar3 = [go.Bar(
        x=df_bar['Year'],
        y=df_bar['Political stability index (-2.5 weak; 2.5 strong)'],
        orientation="v",
        showlegend=False,
        marker=dict(
            color='rgb(239,225,156)',
            line=dict(
                color='rgb(217,240,163)',
                width=12)
        ),
        width=.05
    ),
        go.Scatter(
            x=dff_avg['Year'],
            y=dff_avg['Political stability index (-2.5 weak; 2.5 strong)'],
            showlegend=False,
            mode='lines',
            line=dict(color="#000000", width=2)
        )
    ]


    layout_bar3 = dict(title=dict(text="Political stability",
                                  x=.5, font={"size": 15, 'family':'sans-serif', 'color': '#111'}),
                       xaxis=dict(showline=True,
                                  linecolor="rgb(89, 89, 89)",
                                  tickmode='linear',
                                  tickangle=-90,
                                  tickfont=dict(family="sans-serif", size=12, color='#111')),
                       yaxis=dict(title=dict(text="Stability index (-2.5 weak; 2.5 strong)", font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                  gridcolor="LightGrey",
                                  range=[-2.5, 2.5],
                                  tickfont=dict(family="sans-serif", size=12, color='#111'),
                                  ),
                       paper_bgcolor="#ffffff",
                       plot_bgcolor="#ffffff",
                       barmode='stack'
                       )

    data_bar4 = [go.Bar(
        x=df_bar['Year'],
        y=df_bar['Health spending per capita'],
        orientation="v",
        showlegend=False,
        marker=dict(
            color='rgb(239,225,156)',
            line=dict(
                color='rgb(217,240,163)',
                width=12)
        ),
        width=.05
    ),
        go.Scatter(
            x=dff_avg['Year'],
            y=dff_avg['Health spending per capita'],
            name='Global annual average',
            mode='lines',
            line=dict(color="#000000", width=2)
        )
    ]

    layout_bar4 = dict(title=dict(text='Health spending per capita',
                                  x=.5, font={"size": 15, 'family':'sans-serif', 'color': '#111'}),
                       xaxis=dict(showline=True,
                                  linecolor="rgb(89, 89, 89)",
                                  tickmode='linear',
                                  tickangle=-90,
                                  tickfont=dict(family="sans-serif", size=12, color='#111')),
                       yaxis=dict(title=dict(text="US Dollars", font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                  gridcolor="LightGrey",
                                  range=[0, 10250],
                                  tickfont=dict(family="sans-serif", size=12, color='#111')
                                  ),
                       legend=dict(orientation='h',
                                   yanchor='top',
                                   xanchor='center',
                                   y=-0.3,
                                   x=0.5,
                                   font=dict(family="sans-serif", size=12, color="#111")
                                   ),
                       paper_bgcolor="#ffffff",
                       plot_bgcolor="#ffffff",
                       barmode='stack'
                       )


    trace6 = go.Scatter(
        x=df_bar['Year'],
        y=df_bar['Inflow'],
        name='Inflow',
        mode='lines',
        line=dict(color="#237924", width=2)
    )

    trace7 = go.Scatter(
        x=df_bar['Year'],
        y=df_bar['Outflow'],
        name='Outflow',
        mode='lines',
        line=dict(color="#cc0000", width=2)
    )

    data_line = [trace6, trace7]

    layout_line = dict(title=dict(text='Inflow vs Outlow: ' + str(countries) +
                                       "<br> from " + str(year_aux) + " to " + str(year),
                                  x=.5,
                                  font={"size": 15, 'family':'sans-serif', 'color': '#111'}),
                       xaxis=dict(title=dict(text='Year',font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                  gridcolor="LightGrey",
                                  range=[year_aux, year],
                                  showline=True,
                                  linewidth=1.1,
                                  linecolor="rgb(89, 89, 89)",
                                  tickfont=dict(family="sans-serif", size=12, color='#111'),
                                  tickmode='linear'),
                       yaxis=dict(title=dict(text="Number of migrants",font={"size": 13, 'family':'sans-serif', 'color': '#111'}),
                                  gridcolor="LightGrey",
                                  range=[0, max_in_out],
                                  tickfont=dict(family="sans-serif", size=12, color='#111')
                                  ),
                       legend=dict(orientation='h',
                                   yanchor='top',
                                   xanchor='center',
                                   y=-0.3,
                                   x=0.5,
                                   font=dict(family="sans-serif", size=12, color="#111")
                                   ),
                       paper_bgcolor = "#ffffff",
                       plot_bgcolor="#ffffff"
                       )



    fig_bar2 = go.Figure(data=data_bar, layout=layout_bar)
    fig_bar3 = go.Figure(data=data_bar2, layout=layout_bar2)
    fig_bar4 = go.Figure(data=data_bar3, layout=layout_bar3)
    fig_bar5 = go.Figure(data=data_bar4, layout=layout_bar4)
    fig_line = go.Figure(data=data_line, layout=layout_line)

    return fig_bar2,fig_bar3, fig_bar4, fig_bar5, fig_line



if __name__ == '__main__':
    app.run_server(debug=True)

