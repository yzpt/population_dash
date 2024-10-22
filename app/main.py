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
from layout import create_layout
from scatter_population import plot_historic_population
from load_data import load_data

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
gdf = load_data(precison='100m')
selected_codgeo = ['59','62']
filtered_gdf = gdf[gdf['departement'].isin(selected_codgeo)]
df_historic_population = pd.read_csv('pop_historique_extended.csv', dtype={0: str, 2: str})

def create_layout(
    gdf: gpd.GeoDataFrame,
    fig_map: go.Figure,
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
                                max=100000,
                                step=1000,
                                value=40000,
                                marks={i: str(i) for i in range(0, 100001, 10000)},
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
                                style={'height': '100%'},
                            ),
                        ],
                        xs=12, sm=12, md=6, lg=6, xl=6,
                        style={
                            # "border": "1px solid gray", 
                            "padding": "0px",
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
    max_colorscale: int = 100000,
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
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                tickfont=dict(color='black'),
                titlefont=dict(color='black'),
                x=1,
                y=1,
                xpad=0,
                ypad=30,
                xanchor='right',
                yanchor='top',
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
    )
)

@app.callback(
    [
        Output('map-graph', 'figure'),
    ],
    [
        Input('departement-dropdown', 'value'),
        Input('carto-selection', 'value'),
        Input('geojson-precision', 'value'),
        Input('max-colorscale-slider', 'value'),
    ],
    [
        State('map-graph', 'figure')
    ]
)
def update_map(
    # Inputs
    departement_dropdown: List[str],
    carto_selection: str,
    geojson_precision: str,
    max_colorscale: int,
    
    # States
    fig_map: go.Figure,
    
) -> Tuple[go.Figure]:
    print(f'ctx.triggered_id: {ctx.triggered_id}')
    
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
        filtered_gdf = gdf[gdf['departement'].isin(selected_codgeo)]
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

    # Default return
    return [fig_map]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    