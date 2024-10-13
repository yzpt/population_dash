import geopandas as gpd
import plotly.graph_objects as go
from dash import html, dcc

def create_layout(
    gdf: gpd.GeoDataFrame,
    fig_map: go.Figure,
) -> html.Div:
    return html.Div(
        className='container',
        # style={"height": "100vh"},
        children=[
            html.Div(
                className='left-column',
                children=[

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
                                figure=fig_map,
                                style={"height": "100%"},
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )