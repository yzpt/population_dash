from dash import dash, dcc, html, Input, Output, State, dash_table, callback_context
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import os
import geopandas as gpd


# from layout import create_layout
from map import create_map

def load_data() -> gpd.GeoDataFrame:
    m = 50
    f = '_f'
    print(f'{datetime.now()}: Loading data...')
    gdf = gpd.read_file(f'data/communes_with_population_{m}m{f}.gpkg', layer='communes')
    print(f'Data loaded: {len(gdf)} rows')
    return gdf
gdf = load_data()


# ============================== layout ==============================
import pandas as pd
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
                    # Dropdown filter for regions
                    html.Label("Select Region:"),
                    dcc.Dropdown(
                        id="region-dropdown",
                        options=[{"label": region, "value": region} for region in gdf["region"].unique()],
                        value='32',
                        placeholder="Select a region",
                        clearable=True,
                        multi=True,
                        style=dict(
                            width="100%",
                            color="black",
                        ),
                    ),
                    # Metric display for sum of population
                    html.Div(id="metric-output", style={"margin-top": "20px", "font-size": "20px"}),
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
                                        # bgcolor="rgba(0,0,0,0)",
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
    
    

app = dash.Dash(__name__)
app.layout = create_layout(
    gdf=gdf,
    fig_map=create_map(gdf)
)




# ============================== callbacks ==============================
@app.callback(
    [Output('map-graph', 'figure'), Output('metric-output', 'children')],
    [Input('region-dropdown', 'value')],
)
def update(selected_regions):
    # check selected_regions type
    if isinstance(selected_regions, str):
        selected_regions = [selected_regions]
    elif selected_regions is None:
        selected_regions = []
    
    print(f'selected_regions: {selected_regions}')
    filtered_gdf = gdf[gdf['region'].isin(selected_regions)]
    
    # Update the map based on the selected region
    fig_map = create_map(filtered_gdf)
    
    # # Calculate the sum of population for the filtered region
    total_population = filtered_gdf['pop'].sum()
    metric_text = f"Total Population: {total_population:,}" if selected_regions else "Total Population (All Regions):"
    
    return fig_map, metric_text
    
    # return {}, 'Total Population: 0'


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
