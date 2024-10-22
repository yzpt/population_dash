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
gdf = load_data(precison='100m')
selected_departements = ['59','62']
filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
df_historic_population = pd.read_csv('pop_historique_extended.csv', dtype={0: str, 2: str})

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
                            dcc.Dropdown(
                                id="departement-dropdown",
                                options=[{"label": departement, "value": departement} for departement in gdf["departement"].unique()],
                                value=['59', '62'],
                                placeholder="Select Departments",
                                clearable=True,
                                multi=True,
                                style=dict(color="black"),
                                className="m-3",
                            ),
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
                                        value='100m',
                                    ),
                                ],
                                className="radio-group",
                                style={
                                    'display': 'flex',
                                    'justify-content': 'space-evenly',
                                    },
                            ),
                            dcc.Slider(
                                id='max-colorscale-slider',
                                min=0,
                                max=50000,
                                step=1000,
                                value=25000,
                                marks={i: str(i) for i in range(0, 50001, 10000)},
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
    max_colorscale: int = 25000,
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
            z=gdf['pop'],
            colorscale=colorscale_palette,
            zmin=min_colorscale,
            zmax=max_colorscale,
            marker_opacity=marker_opacity,
            marker_line_width=0,
            showlegend=False,
            text=gdf['nom'],
            customdata=gdf['codgeo'],
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
        mapbox_zoom=7,
        mapbox_center={"lat": 50.62925, "lon": 3.057256},
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
        gdf=filtered_gdf,
        mapbox_access_token=mapbox_access_token,
        mapbox_style='open-street-map',
    ),
    fig_timeline=plot_historic_population(
        df_historic_population=df_historic_population,
        departements_list=selected_departements
    )
)

@app.callback(
    [
        Output('map-graph', 'figure'),
        Output('timeline-graph', 'figure')
    ],
    [
        Input('departement-dropdown', 'value'),
        Input('carto-selection', 'value'),
        Input('geojson-precision', 'value'),
        Input('max-colorscale-slider', 'value'),
        Input('map-graph', 'hoverData'),
    ],
    [
        State('map-graph', 'figure'),
        State('timeline-graph', 'figure')
    ]
)
def update_map(
    # Inputs
    departement_dropdown: List[str],
    carto_selection: str,
    geojson_precision: str,
    max_colorscale: int,
    map_hover_data: Dict[str, Any],
    
    # States
    fig_map: go.Figure,
    fig_timeline: go.Figure,
    
) -> Tuple[go.Figure]:
    print(f'ctx.triggered_id: {ctx.triggered_id}')
    print(f'map_hover_data: {map_hover_data}')
    
    # Update selected departments
    if ctx.triggered_id == 'departement-dropdown':
        global gdf
        filtered_gdf = gdf[gdf['departement'].isin(departement_dropdown)]
        fig_map = go.Figure(fig_map)
        fig_map.update_traces(
            geojson=filtered_gdf.__geo_interface__,
            locations=filtered_gdf.index,
            z=filtered_gdf['pop'],
            text=filtered_gdf['nom'],
            customdata=filtered_gdf['codgeo'],
        )
    
    # Update map style
    if ctx.triggered_id == 'carto-selection':
        fig_map = go.Figure(fig_map).update_layout(mapbox_style=carto_selection)
    
    # Update geojson precision
    if ctx.triggered_id == 'geojson-precision':
        gdf = load_data(precison=geojson_precision)
        filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
        fig_map = go.Figure(fig_map)
        fig_map.update_traces(
            geojson=filtered_gdf.__geo_interface__,
            locations=filtered_gdf.index,
            z=filtered_gdf['pop'],
            text=filtered_gdf['nom'],
            customdata=filtered_gdf['codgeo'],
        )

    # Update colorscale
    if ctx.triggered_id == 'max-colorscale-slider':
        fig_map = go.Figure(fig_map)
        fig_map.update_traces(
            zmax=max_colorscale,
        )
        
    # City hover
    if ctx.triggered_id == 'map-graph' and map_hover_data is not None:
            print(f'---city hover triggered---')
            global df_historic_population
            hovered_codgeo = map_hover_data['points'][0]['customdata']
            fig_timeline = plot_historic_population(
                df_historic_population=df_historic_population,
                codgeo=hovered_codgeo
            )
            
    # Default return
    return [
        fig_map,
        fig_timeline,
        ]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    