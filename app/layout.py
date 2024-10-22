import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
import geopandas as gpd

def create_layout(
    gdf: gpd.GeoDataFrame,
    fig_map: go.Figure,
) -> html.Div:
    return html.Div(
        className='container',
        children=[
            html.Div(
                className='left-column',
                children=[
                    # Dropdown filter for departements
                    html.Div(id='infos-box', children=[]),
                    dcc.RadioItems(
                        id='filtering-mode',
                        options=[
                            {'label': 'Windows-filtering mode', 'value': 'windows-filtering-mode'},
                            {'label': 'BUG: Box-select mode', 'value': 'box-select-mode'},
                            # {'label': 'Lasso-select mode', 'value': 'lasso-select-mode'},
                            {'label': 'Hover-click-mode', 'value': 'hover-click-mode'},
                        ],
                        value='hover-click-mode',
                        style={"flex-direction": "row"},
                    ),
                    html.Button('Select All', id='select-all-button', n_clicks=0, style={"visibility": "hidden"}),
                    html.Label("Départements:"),
                    dcc.Dropdown(
                        id="departement-dropdown",
                        options=[{"label": departement, "value": departement} for departement in gdf["departement"].unique()],
                        # value=[ '62'], 
                        value=['59', '62'], 
                        placeholder="Départements",
                        clearable=True,
                        multi=True,
                        style=dict(
                            width="100%",
                            color="black",
                        ),
                    ),
                    
                    html.Div(
                        style={"display": "flex", "flex-direction": "row", 'width': '100%', 'justify-content': 'space-between'},
                        children=[
                            html.Div(
                                style={"display": "flex", "flex-direction": "column", 'flex': '1'},
                                children=[
                                    html.Label("Max Colorscale Value:", style={"margin": "auto"}),
                                    # slider for max colorscale value
                                    dcc.Slider(
                                        id='colorscale-max-slider',
                                        min=0,
                                        max=100000,  # Set based on your data range
                                        step=1000,
                                        value=30000,  # Default max value
                                        marks=None,
                                        tooltip={"placement": "bottom", "always_visible": True},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"display": "flex", "flex-direction": "column", 'flex': '1'},
                                children=[
                                    html.Label("Opacity:"),
                                    dcc.Slider(
                                        id='slider-marker-opacity',
                                        min=0,
                                        max=1,
                                        step=0.1,
                                        value=0.5,
                                        marks={i: str(i) for i in [0, 0.5, 1]},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Slider for max colorscale value
                    # radios for mapbox_style
                    # "open-street-map", "carto-positron", and "carto-darkmatter" yield maps composed of raster tiles from various public tile servers which do not require signups or access tokens.
                    # "basic", "streets", "outdoors", "light", "dark", "satellite", or "satellite-streets" yield maps composed of vector tiles from the Mapbox service, and do require a Mapbox Access Token or an on-premise Mapbox installation.
                    html.Div(
                        style={"display": "flex", "flex-direction": "row"},
                        children=[
                            html.Label("map style:"),
                            dcc.RadioItems(
                                id='mapbox-style-radio',
                                inline=True,
                                options=[
                                    {'label': 'Open Street Map', 'value': 'open-street-map'},
                                    {'label': 'Carto Positron', 'value': 'carto-positron'},
                                    {'label': 'Carto Darkmatter', 'value': 'carto-darkmatter'},
                                ],
                                value='carto-darkmatter',
                                labelStyle={'display': 'inline-block'},
                            ),
                        ]
                    ),
                    
                    
                    dcc.Dropdown(
                        id="colorscale-palette-dropdown",
                        options=[
                            {"label": "Viridis", "value": "Viridis"},
                            {"label": "Cividis", "value": "Cividis"},
                            {"label": "Plasma", "value": "Plasma"},
                            {"label": "Inferno", "value": "Inferno"},
                            {"label": "Magma", "value": "Magma"},
                            {"label": "Greens", "value": "Greens"},
                            {"label": "Blues", "value": "Blues"},
                        ],
                        value="Viridis",  # Default color scale
                        clearable=False,
                        style=dict(width="100%", color="black", visibility="hidden"),
                    ),
                    # dcc buttons form for shapegile precision
                    html.Div(
                        className='geojson-precision',
                        style={"display": "flex", "flex-direction": "row"},
                        children=[
                            html.Label("GeoJSON precision:"),
                            dcc.RadioItems(
                                id='geojson-precision-radio',
                                inline=True,
                                options=[
                                    {'label': '5m', 'value': '5m'},
                                    {'label': '50m', 'value': '50m'},
                                    {'label': '100m', 'value': '100m'},
                                    {'label': '1000m', 'value': '1000m'},
                                ],
                                value='100m',
                                labelStyle={'display': 'inline-block'},
                            ),
                        ]
                    ),
                    
                    html.Div(id="metric-output", style={"margin-top": "20px", "font-size": "20px"}),
                    html.P(' '),
                    dcc.Graph(
                        id='historic-population-graph',
                        config=dict(scrollZoom=True),
                        figure=go.Figure(
                            layout=dict(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                xaxis=dict(visible=False),
                                yaxis=dict(visible=False),
                            )
                        ),
                        style={"height": "25%"},
                    ),
                    
                ]
            ),
            # Right column with graphs
            html.Div(
                className='right-column',
                children=[
                    html.Div(
                        className='map-graph-container',
                        children=[
                            dcc.Graph(
                                id='map-graph',
                                className='map-graph',
                                config=dict(scrollZoom=True),
                                figure=go.Figure(
                                    layout=dict(
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                    )
                                ),
                                style={"height": "100%"},
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )
