from dash import dash, dcc, html, Input, Output, State, dash_table, ctx
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




# === global variables =============================================================================
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
selected_codgeo = None
gdf = load_data(precison='100m')
gdf['opacity'] = 0.5
filtered_gdf = gdf[gdf['departement'].isin(['32'])]
df_historic_population = pd.read_csv('pop_historique_extended.csv', dtype={0: str, 2: str})
# ==================================================================================================


# === initialize the app ==========================================================================
app = dash.Dash(__name__)
app.layout = create_layout(
    gdf=gdf,
    fig_map=create_map(
        gdf=filtered_gdf,
        mapbox_access_token=mapbox_access_token,
    )
)
# ==================================================================================================




# ============================== callbacks ==============================
@app.callback(
    [
        Output('map-graph', 'figure'), Output('metric-output', 'children'),
        Output('infos-box', 'children'),
    ],
    [
        Input('departement-dropdown', 'value'),
        Input('colorscale-max-slider', 'value'),
        Input('colorscale-palette-dropdown', 'value'),
        Input('geojson-precision-radio', 'value'),
        Input('slider-marker-opacity', 'value'),
        Input('mapbox-style-radio', 'value'),
        Input('select-all-button', 'n_clicks'),
        Input('map-graph', 'relayoutData'),
        Input('windows-filtering-mode', 'value'),
    ],
    [
        State('map-graph', 'figure')
    ],
    # prevent_initial_call=True
)
def update(
    # Inputs
    selected_departements: List[str],
    max_colorscale: int,
    colorscale_palette: str,
    geojson_precision: str,
    slider_marker_opacity: float,
    mapbox_style: str,
    n_clicks_select_all_markers: int,
    map_relayout_data: Dict[str, Any],
    windows_filtering_mode: bool,
    # States
    current_figure: Dict[str, Any],
    prevent_initial_call: bool = True,
) -> Tuple[go.Figure, str]:
    
    # ================ #
    global gdf
    global pre_filtered_gdf
    global filtered_gdf
    # ================ #
    
    if ctx.triggered[0]['prop_id'] == 'geojson-precision-radio.value':
        print('---load_data()')
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
    
    if ctx.triggered[0]['prop_id'] == 'departement-dropdown.value' or ctx.triggered[0]['prop_id'] == '.':
        pre_filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
        filtered_gdf = pre_filtered_gdf.copy()
    
    if windows_filtering_mode:
        if map_relayout_data:
            if map_relayout_data and 'mapbox._derived' in map_relayout_data:
                lon_min, lat_min = map_relayout_data['mapbox._derived']['coordinates'][3]
                lon_max, lat_max = map_relayout_data['mapbox._derived']['coordinates'][1]
                bounding_box = box(lon_min, lat_min, lon_max, lat_max)
                box_df = gpd.GeoDataFrame(geometry=[bounding_box], crs='EPSG:4326')
                filtered_gdf = gpd.sjoin(pre_filtered_gdf, box_df, how='inner', predicate='within')

    # Update the map based on the selected departement and colorscale
    fig_map = create_map(
        gdf=filtered_gdf, 
        max_colorscale=max_colorscale,
        colorscale_palette=colorscale_palette,
        marker_opacity=slider_marker_opacity,
        mapbox_style=mapbox_style,
        mapbox_access_token=mapbox_access_token,
    )  
    fig_map.update_layout(mapbox_zoom=zoom, mapbox_center=center)
    if (n_clicks_select_all_markers > 0
        or ctx.triggered[0]['prop_id'] == '.'
        or ctx.triggered[0]['prop_id'] == 'departement-dropdown.value'):
        fig_map.update_traces(selectedpoints=list(range(len(gdf))))  # Select all points
    
    total_population = filtered_gdf['pop'].sum()
    metric_text = f"Total Population: {total_population:,}" if selected_departements else "Total Population (All departements):"
    
    # s = ', '.join(filtered_gdf['nom'].unique())
    s=''
    
    return fig_map, metric_text, s


is_freezed = False
freezed_codgeo = '59350'

@app.callback(
    [
        Output('historic-population-graph', 'figure'),
    ],
    [
        Input('map-graph', 'hoverData'),
        Input('map-graph', 'clickData'),
        Input('map-graph', 'selectedData'),
        Input('select-all-button', 'n_clicks'),
    ],
    [
        State('historic-population-graph', 'figure'),
        State('windows-filtering-mode', 'value'),
    ]
)
def update_historic_population_graph(
    hover_data: dict,
    click_data: dict,
    selected_data: dict,
    select_all_button: int,
    current_figure: go.Figure,
    windows_filtering_mode: bool,
) -> go.Figure:
    global is_freezed
    global freezed_codgeo
    global filtered_gdf
    global df_historic_population
    
    print(f'---')
    
    print(f'--windows_filtering_mode: {windows_filtering_mode}')
    if windows_filtering_mode:
        codgeo_list = filtered_gdf['codgeo'].tolist()
        print(f'codgeo_list: {codgeo_list}')
        return [plot_historic_population(
                    df_historic_population=df_historic_population,
                    codgeo_list=codgeo_list
                )]
    
    if selected_data:
        print('---selected_data')
        codgeo_list = pd.DataFrame(selected_data["points"])["customdata"].to_list()
        print(f'codgeo_list: {codgeo_list}')
        # update trace map, lower opacity of unselected points
        filtered_gdf['opacity'] = 0.1
        filtered_gdf.loc[filtered_gdf['codgeo'].isin(codgeo_list), 'opacity'] = 0.5

        return [plot_historic_population(
                    df_historic_population=df_historic_population,
                    codgeo_list=codgeo_list
                )]
    
    
    
    # print('--------map-graph-data')
    # print(f'hover_data: {hover_data}')  
    # print(f'click_data: {click_data}')
    # print(f'len(selected_data["points"]): {len(selected_data["points"])}' if selected_data else 'selected_data is None')
    
    # codgeo_list = [codgeo for codgeo in selected_data['points'][0]['customdata']] if selected_data else []
    # print(f'codgeo_list: {codgeo_list}')
    # print(f'select_data["points"]: {selected_data["points"]}' if selected_data else 'selected_data is None')
    # selected_codgeo_list = [point['customdata'] for point in selected_data['points']] if selected_data else []
    # if selected_codgeo_list:
    #     return plot_historic_population(codgeo_list=selected_codgeo_list)
    
    
    return [go.Figure()]
    
    
    



    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
