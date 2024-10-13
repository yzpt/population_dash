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
# from fig_map import create_map_figure

# Data ============================================================================= Data ===========
print(f'{datetime.now()}: Loading data...')

m = 50
f = ''
gdf = gpd.read_file(f'data/communes_with_population_{m}m{f}.gpkg', layer='communes')
print(f'Data loaded: {len(gdf)} rows')



fig_map = go.Figure()

fig_map.add_trace(
    go.Choroplethmapbox(
        geojson=gdf.__geo_interface__,
        locations=gdf.index,         # The feature's array of locations
        z=gdf['pop'],       # The values you want to display in the choropleth
        colorscale="Viridis",        # Choose your color scale
        # ajdust color range
        zmin=0,
        zmax=100000,
        marker_opacity=0.5,
        marker_line_width=0,
        showlegend=False,
        text=gdf['nom'],
        hoverinfo='text+z',
        showscale=False,
    )
)

# Set up the map layout
fig_map.update_layout(
    mapbox_style="carto-darkmatter",
    mapbox_zoom=7,              # Set zoom level
    mapbox_center={"lat": 50.5, "lon": 2.8},  # Center on the map
    margin={"r":0,"t":0,"l":0,"b":0},
    plot_bgcolor='#333333',
    paper_bgcolor='#333333',
    # legend=dict(
    #     title='Population',
    #     bgcolor='#333333',
    #     bordercolor='#333333',
    #     font=dict(color='white'),
    # ),
    font=dict(color='white'),
    showlegend=False,
)




# Layout =========================================================================== Layout =========
def create_layout(
    df: pd.DataFrame,
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




# ================================================================================== app ==========
app = dash.Dash(__name__)

app.layout = create_layout(
    df=pd.DataFrame(),
    fig_map=fig_map,
)


# ================================================================================== Callbacks =====















# ================================================================================== run ==========
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
