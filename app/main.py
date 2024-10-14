from dash import dash, dcc, html, Input, Output, State, dash_table, ctx
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import os
import geopandas as gpd

from dotenv import load_dotenv
load_dotenv()

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

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
                    # Slider for max colorscale value
                    html.Label("Max Colorscale Value:"),
                    # slider for max colorscale value
                    dcc.Slider(
                        id='colorscale-max-slider',
                        min=0,
                        max=100000,  # Set based on your data range
                        step=1000,
                        value=30000,  # Default max value
                        marks={i: str(i) for i in range(0, 100001, 10000)},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
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
                    html.Hr(),
                    html.P('ajotuer stadia maps'),
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

    
# ============================== map ==============================
import geopandas as gpd
import plotly.graph_objects as go

def create_map(
    gdf: gpd.GeoDataFrame,
    min_colorscale: int = 0,
    max_colorscale: int = 100000,
    colorscale_palette: str = "Viridis",
    marker_opacity: float = 0.5,
    mapbox_style: str = "carto-darkmatter",
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

gdf = load_data(precison='1000m')
filtered_gdf = gdf[gdf['departement'].isin(['32'])]

df_historic_population = pd.read_csv('pop_historique_extended.csv', dtype={0: str, 2: str})

app = dash.Dash(__name__)
app.layout = create_layout(
    gdf=gdf,
    fig_map=create_map(filtered_gdf)
)

# ============================== graph ==============================
import plotly.graph_objects as go
import pandas as pd

def plot_historic_population(codgeo: str) -> go.Figure:
    global df_historic_population
    
    # Filter and transpose the DataFrame
    df = df_historic_population[df_historic_population['codgeo'] == codgeo].T.reset_index()[3:]
    
    # Extract the name of the region or city
    nom = df.iloc[0, 1]
    
    # Clean and rename columns
    df = df[1:]
    df.columns = ['year', 'population']
    
    # Convert 'year' to datetime
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    
    # Sort values by year
    df.sort_values('year', ascending=True, inplace=True)
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot with lines and markers
    fig.add_trace(
        go.Scatter(
            x=df['year'],
            y=df['population'],
            mode='lines+markers',
            line_shape='spline',
        )
    )
    
    # Update layout with titles and styling
    fig.update_layout(
        title=dict(
            text=f'{nom}',
            x=.95,
            y=0.95,
            xanchor='right',
            yanchor='top',
        ),
        yaxis_title='Population',
        xaxis=dict(type='date'),
        template='plotly_dark',
        margin={"r":10,"t":30,"l":10,"b":10},
        height=200
    )

    return fig



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
        Input('slider-marker-opacity', 'value'),
        Input('mapbox-style-radio', 'value'),
        
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
    marker_opacity: float,
    mapbox_style: str,
    # States
    current_figure: Dict[str, Any],
) -> Tuple[go.Figure, str]:
    
    # ================ #
    global gdf
    # print('---------------------------------')
    # print(f'ctx.triggered: {ctx.triggered}')
    # print(f'mapbox_style: {mapbox_style}')
    # ================ #
    
    if geojson_precision:
        gdf = load_data(
            precison=geojson_precision,
        )
    
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
        colorscale_palette=colorscale_palette,
        mapbox_style=mapbox_style,
        marker_opacity=marker_opacity,
    )  
    # Set the zoom and center back to the figure
    fig_map.update_layout(mapbox_zoom=zoom, mapbox_center=center)

    total_population = filtered_gdf['pop'].sum()
    metric_text = f"Total Population: {total_population:,}" if selected_departements else "Total Population (All departements):"
    
    return fig_map, metric_text


is_freezed = False
freezed_codgeo = '59350'

@app.callback(
    Output('historic-population-graph', 'figure'),
    [
        Input('map-graph', 'hoverData'),
        Input('map-graph', 'clickData'),
    ],
    [
        State('historic-population-graph', 'figure'),
    ]
)
def update_historic_population_graph(
    hover_data: dict,
    click_data: dict,
    current_figure: go.Figure,
):
    global is_freezed
    global freezed_codgeo
    
    if not click_data and not hover_data:
        return plot_historic_population(codgeo='59350')
    
    if not is_freezed:
        if hover_data and hover_data == click_data:
            is_freezed = True
            freezed_codgeo = click_data['points'][0]['customdata']
            return plot_historic_population(freezed_codgeo)
    
    if is_freezed:
        if click_data and click_data == hover_data:
            is_freezed = False
            freezed_codgeo = None
            codgeo = click_data['points'][0]['customdata']
            return plot_historic_population(codgeo)
        return current_figure
    
    if hover_data:
        hovered_codgeo = hover_data['points'][0]['customdata']
        return plot_historic_population(hovered_codgeo)
    
    return go.Figure()
    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
