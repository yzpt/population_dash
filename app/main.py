from dash import dash, dcc, html, Input, Output, State, dash_table, ctx
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import os
import geopandas as gpd



def load_data(
    precison: str = '1000m',
) -> gpd.GeoDataFrame:
    f = 'f'
    print(f'{datetime.now()}: Loading data from communes_with_population_{precison}_{f}.gpkg')
    gdf = gpd.read_file(f'communes_with_population_{precison}_{f}.gpkg')
    print(f'Data loaded: {len(gdf)} rows')
    return gdf


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
        children=[
            html.Div(
                className='left-column',
                children=[
                    # Dropdown filter for departements
                    html.Label("Select departement:"),
                    dcc.Dropdown(
                        id="departement-dropdown",
                        options=[{"label": departement, "value": departement} for departement in gdf["departement"].unique()],
                        value=['59', '62'], 
                        placeholder="Département:",
                        clearable=True,
                        multi=True,
                        style=dict(
                            width="100%",
                            color="black",
                        ),
                    ),
                    # Slider for max colorscale value
                    html.Label("Max Colorscale Value:"),
                    # slider for max colorscale value
                    dcc.Slider(
                        id='colorscale-max-slider',
                        min=0,
                        max=100000,  # Set based on your data range
                        step=1000,
                        value=100000,  # Default max value
                        marks={i: str(i) for i in range(0, 100001, 10000)},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    # dcc.RangeSlider(
                    #     id='colorscale-range-slider',
                    #     min=0,
                    #     max=100000,  # Set based on your data range
                    #     step=1000,
                    #     value=[0, 100000],  # Default range
                    #     marks={i: str(i) for i in range(0, 100001, 10000)},
                    #     tooltip={"placement": "bottom", "always_visible": True},
                    # ),
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
                        value="Cividis",  # Default color scale
                        clearable=False,
                        style=dict(width="100%", color="black"),
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
                                value='1000m',
                                labelStyle={'display': 'inline-block'},
                            ),
                        ]
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

    
# ============================== map ==============================
import geopandas as gpd
import plotly.graph_objects as go

def create_map(
    gdf: gpd.GeoDataFrame,
    min_colorscale: int = 0,
    max_colorscale: int = 100000,
    colorscale_palette: str = "Cividis"  # New parameter for color scale
) -> go.Figure:
    fig_map = go.Figure()

    fig_map.add_trace(
        go.Choroplethmapbox(
            geojson=gdf.__geo_interface__,
            locations=gdf.index,
            z=gdf['pop'],
            colorscale=colorscale_palette,  # Use the selected color scale
            zmin=min_colorscale,
            zmax=max_colorscale,
            marker_opacity=0.5,
            marker_line_width=0,
            showlegend=False,
            text=gdf['nom'],
            hoverinfo='text+z',
            showscale=True,
            colorbar=dict(
                title='Population',
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                tickfont=dict(color='white'),
                titlefont=dict(color='white'),
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
        mapbox_style="carto-darkmatter",
        mapbox_zoom=7,
        mapbox_center={"lat": 50.62925, "lon": 3.057256},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
    )
    
    return fig_map

gdf = load_data(
    precison='1000m'
)
   
filtered_gdf = gdf[gdf['departement'].isin(['32'])]

app = dash.Dash(__name__)
app.layout = create_layout(
    gdf=gdf,
    fig_map=create_map(filtered_gdf)
)




# ============================== callbacks ==============================
@app.callback(
    [
        Output('map-graph', 'figure'), Output('metric-output', 'children')
    ],
    [
        Input('departement-dropdown', 'value'),
        # Input('colorscale-range-slider', 'value'),
        Input('colorscale-max-slider', 'value'),
        Input('colorscale-palette-dropdown', 'value'),
        Input('geojson-precision-radio', 'value'),
        
    ],
    [
        State('map-graph', 'figure')
    ],
    # prevent_initial_call=True
)
def update(
    # Inputs
    selected_departements: List[str],
    # colorscale_range: Tuple[int, int],
    max_colorscale: int,
    colorscale_palette: str,
    geojson_precision: str,
    # States
    current_figure: Dict[str, Any],
) -> Tuple[go.Figure, str]:
    
    # ================ #
    global gdf
    print(f'ctx.triggered: {ctx.triggered}')
    # ================ #
    
    # Case button geojson-precision-radio.value is triggered
    if ctx.triggered:
        if ctx.triggered[0]['prop_id'] == 'geojson-precision-radio.value':
            geojson_precision = ctx.triggered[0]['value']
            print(f'geojson_precision: {geojson_precision}')
            gdf = load_data(
                precison=geojson_precision,
            )
            print(f'gdf: {len(gdf)} rows')
    
    
    # Extract the current zoom and center from the figure
    zoom = current_figure['layout']['mapbox']['zoom'] if 'mapbox' in current_figure['layout'] else 7
    center = current_figure['layout']['mapbox']['center'] if 'mapbox' in current_figure['layout'] else {"lat": 50.62925, "lon": 3.057256}

    if isinstance(selected_departements, str):
        selected_departements = [selected_departements]
    elif selected_departements is None:
        selected_departements = []
    
    # min_colorscale, max_colorscale = colorscale_range  
    max_colorscale = max_colorscale
    
    filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
    
    # Update the map based on the selected departement and colorscale
    fig_map = create_map(
        gdf=filtered_gdf, 
        # min_colorscale=min_colorscale, 
        max_colorscale=max_colorscale,
        colorscale_palette=colorscale_palette
    )  
    # Set the zoom and center back to the figure
    fig_map.update_layout(mapbox_zoom=zoom, mapbox_center=center)

    total_population = filtered_gdf['pop'].sum()
    metric_text = f"Total Population: {total_population:,}" if selected_departements else "Total Population (All departements):"
    
    return fig_map, metric_text



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
