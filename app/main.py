from dash import dash, dcc, html, Input, Output, State, dash_table, ctx, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import os
import geopandas as gpd
from shapely.geometry import box  # Import box from shapely.geometry

from dotenv import load_dotenv
load_dotenv()

from map import create_map
# from layout import create_layout
from scatter_population import plot_historic_population
from load_data import load_data

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
gdf = load_data(
    precison='1000m',
    type='departements',
)

def create_layout(
    gdf: gpd.GeoDataFrame,
    fig_map: go.Figure,
    fig_timeline: go.Figure,
) -> html.Div:
    return dbc.Container(
        [   
            dbc.Row(
                style={'height': '100vh'},
                children=
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        id="carto-selection",
                                        className="btn-group",
                                        inputClassName="btn-check",
                                        labelClassName="btn btn-outline-primary",
                                        labelCheckedClassName="active",
                                        options=[
                                            {"label": "Open Street Map", "value": "open-street-map"},
                                            {"label": "Positron", "value": "carto-positron"},
                                            {"label": "Dark", "value": "carto-darkmatter"},
                                        ],
                                        value='open-street-map',
                                    ),
                                ],
                                className="radio-group m-2",
                                style={
                                    'display': 'flex',
                                    'justify-content': 'space-evenly',
                                    },
                            ),
                            html.Div(
                                dbc.RadioItems(
                                        id="geojson-precision",
                                        className="btn-group",
                                        inputClassName="btn-check",
                                        labelClassName="btn btn-outline-primary",
                                        labelCheckedClassName="active",
                                        options=[
                                            {"label": "5m", "value": "5m"},
                                            {"label": "50m", "value": "50m"},
                                            {"label": "100m", "value": "100m"},
                                            {"label": "1000m", "value": "1000m"},
                                        ],
                                        value='1000m',
                                    ),
                                className="radio-group m-2",
                                style={
                                    'display': 'flex',
                                    'justify-content': 'space-evenly',
                                    },
                            ),
                            dcc.Slider(
                                id='max-colorscale-slider',
                                min=0,
                                max=3e6,
                                step=1e5,
                                value=2e6,
                                marks={i: str(i) for i in range(0, int(3e6), int(5e5))},
                                className="m-3",
                            ),
                            dcc.Graph(
                                id='bars-graph',
                                figure=go.Figure(),
                            ),
                            dcc.Slider(
                                id='max-population-range-slider',
                                min=0,
                                max=4e5,
                                value=4e5,
                                marks={i: str(i) for i in range(0, int(4e5), int(1e5))},
                                className="m-3",
                            ),
                        ],
                        xs=12, sm=12, md=6, lg=6, xl=6,
                        style={
                            # "border": "1px solid gray", 
                            "padding": "0px",
                            "align-items": "center",
                        },
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(
                                figure=fig_map, 
                                id='map-graph', 
                                config={'scrollZoom': True},
                                style={
                                    'flex': '3',
                                    'width': '100%'
                                },
                            ),
                            dcc.Graph(
                                id='timeline-graph',
                                figure=fig_timeline,
                                style={
                                    'flex': '1',
                                    'width': '100%'
                                },
                            )
                        ],
                        xs=12, sm=12, md=6, lg=6, xl=6,
                        style={
                            # "border": "1px solid gray", 
                            "padding": "0px",
                            # "width": "100%",
                            "display": "flex",
                            "flex-direction": "column",
                            "align-items": "flex-start",
                        },
                    ),
                ],
            ),
        ],
        fluid=True,
    )


def create_map(
    gdf: gpd.GeoDataFrame,
    min_colorscale: int = 0,
    max_colorscale: int = 2e6,
    colorscale_palette: str = "Viridis",
    marker_opacity: float = 0.5,
    mapbox_style: str = "carto-darkmatter",
    mapbox_access_token: str = None,
) -> go.Figure:
    fig_map = go.Figure()

    fig_map.add_trace(
        go.Choroplethmapbox(
            geojson=gdf.__geo_interface__,
            locations=gdf.index,
            z=gdf['fh_total'],
            colorscale=colorscale_palette,
            zmin=min_colorscale,
            zmax=max_colorscale,
            marker_opacity=marker_opacity,
            marker_line_width=0,
            showlegend=False,
            text=gdf['nom'],
            customdata=gdf['code_dep'],
            hoverinfo='text+z',
            showscale=True,
            colorbar=dict(
                title='Population',
                bgcolor='white',
                # bordercolor='white',
                # bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                tickfont=dict(color='black'),
                titlefont=dict(color='black'),
                x=1,
                y=0,
                xpad=10,
                ypad=10,
                xanchor='right',
                yanchor='bottom',
                len=0.5,
            ),
        )
    )

    # Set up the map layout
    fig_map.update_layout(
        mapbox_style=mapbox_style,
        mapbox_accesstoken=mapbox_access_token,
        # mapbox_zoom=7,
        # mapbox_center={"lat": 50.62925, "lon": 3.057256},
        mapbox_zoom=4.5,
        mapbox_center={"lat": 46.95332, "lon": 3.05951},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
    )
    
    return fig_map





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = create_layout(
    gdf=gdf,
    fig_map=create_map(
        gdf=gdf,
        mapbox_access_token=mapbox_access_token,
        mapbox_style='open-street-map',
    ),
    # fig_timeline=plot_historic_population(
    #     df_historic_population=df_historic_population,
    #     departements_list=selected_departements
    # )
    fig_timeline=go.Figure()
)

@app.callback(
    [
        Output('map-graph', 'figure'),
        Output('timeline-graph', 'figure'),
        Output('bars-graph', 'figure'),
    ],
    [
        # Input('departement-dropdown', 'value'),
        Input('carto-selection', 'value'),
        Input('geojson-precision', 'value'),
        Input('max-colorscale-slider', 'value'),
        Input('map-graph', 'hoverData'),
        Input('map-graph', 'relayoutData'),
        Input('max-population-range-slider', 'value'),
    ],
    [
        State('map-graph', 'figure'),
        State('timeline-graph', 'figure'),
        State('bars-graph', 'figure'),
    ]
)
def update_map(
    # Inputs
    # departement_dropdown: List[str],
    carto_selection: str,
    geojson_precision: str,
    max_colorscale: int,
    map_hover_data: Dict[str, Any],
    map_relayout_data: Dict[str, Any],
    max_population_range: int,
    
    # States
    fig_map: go.Figure,
    fig_timeline: go.Figure,
    fig_pyramid: go.Figure,
    
) -> Tuple[go.Figure, go.Figure, go.Figure]:
    print(f'ctx.triggered_id: {ctx.triggered_id}')
    print(f'map_relayout_data: {map_relayout_data}')
    print(f'map_hover_data: {map_hover_data}')
    global gdf
    print(f'gdf: {gdf.columns}')
    
        
    # Update map style
    if ctx.triggered_id == 'carto-selection':
        fig_map = go.Figure(fig_map).update_layout(mapbox_style=carto_selection)
    
    # Update geojson precision
    if ctx.triggered_id == 'geojson-precision':
        gdf = load_data(precison=geojson_precision)
        # filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
        fig_map = go.Figure(fig_map)
        fig_map.update_traces(
            geojson=gdf.__geo_interface__,
            locations=gdf.index,
            z=gdf['fh_total'],
            text=gdf['nom_dep'],
            customdata=gdf['code_dep'],
        )

    # Update colorscale
    if ctx.triggered_id == 'max-colorscale-slider':
        fig_map = go.Figure(fig_map)
        fig_map.update_traces(
            zmax=max_colorscale,
        )
        
    # City hover
    # if ctx.triggered_id == 'map-graph' and map_hover_data is not None:
    #         print(f'---city hover triggered---')
    #         global df_historic_population
    #         hovered_codgeo = map_hover_data['points'][0]['customdata']
    #         # transform historic population data
    #         df = df_historic_population[df_historic_population['codgeo'] == hovered_codgeo]
    #         df = df.T[4:]
    #         df['population'] = df.sum(axis=1)
    #         df.reset_index(inplace=True)
    #         df.rename(columns={'index':'year'}, inplace=True)
    #         df = df[['year','population']].reset_index(drop=True)
    #         df['year'] = pd.to_datetime(df['year'], format='%Y')
            
    #         fig_timeline = go.Figure(fig_timeline)
    #         fig_timeline.update_traces(
    #             x=df['year'],
    #             y=df['population'],
    #         )
    
    # departement hover
    if ctx.triggered_id == 'map-graph' and map_hover_data is not None:
        print('---- hover departement ----')
        code_dep = map_hover_data['points'][0]['customdata']
        df = gdf.drop(columns=['geometry']).loc[gdf['code_dep'] == code_dep]
        df = df.T[5:].reset_index()
        df.columns = ['categorie', 'population']
        df = df[6:]
        df.reset_index(drop=True, inplace=True)
        pyramid_df = pd.DataFrame(columns=['tranche_age', 'population_femmes', 'population_hommes'])
        pyramid_df['tranche_age'] = ['0-19', '20-39', '40-59', '60-74', '75+']
        pyramid_df['population_hommes'] = df['population'][:5].values.astype(int)
        pyramid_df['population_femmes'] = df['population'][6:-1].values.astype(int)
        
        fig_pyramid = go.Figure()
        fig_pyramid.add_trace(
            go.Bar(
                x=pyramid_df['population_hommes'],
                y=pyramid_df['tranche_age'],
                name='Hommes',
                orientation='h',
                hoverinfo='none',
            )
        )
        fig_pyramid.add_trace(
            go.Bar(
                x=pyramid_df['population_femmes'] * -1,
                y=pyramid_df['tranche_age'],
                name='Femmes',
                orientation='h',
                hoverinfo='none',
            )
        )
        fig_pyramid.update_layout(
            title='Population par tranche d\'âge et par sexe',
            barmode='overlay',
            xaxis_title='Population',
            yaxis_title='Age',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
            ),
            xaxis=dict(
                range=[-max_population_range, max_population_range],
            ),
            template='plotly_white',
            height=300,
            
        )
        # return [
        #     fig_map,
        #     fig_timeline,
        #     fig_pyramid,
        # ]  
        
    
    if ctx.triggered_id == 'max-population-range-slider':
        fig_pyramid = go.Figure(fig_pyramid)
        fig_pyramid.update_layout(
            xaxis=dict(
                range=[-max_population_range, max_population_range],
            ),
        )
        
        
        
        
            
    # Default return
    return [
        fig_map,
        fig_timeline,
        fig_pyramid,
        ]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    