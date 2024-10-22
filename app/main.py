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



init = True
# ============================== callbacks ==============================
@app.callback(
    [
        Output('map-graph', 'figure'), 
        Output('historic-population-graph', 'figure'),
        Output('metric-output', 'children'),
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
        Input('filtering-mode', 'value'),
        Input('map-graph', 'relayoutData'),
        Input('map-graph', 'clickData'),
        Input('map-graph', 'selectedData'),
        Input('map-graph', 'hoverData'),
        
    ],
    [
        State('map-graph', 'figure'),
        State('historic-population-graph', 'figure'),
    ],
    prevent_initial_call=True
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
    filtering_mode: bool,
    map_relayout_data: Dict[str, Any],
    map_click_data: Dict[str, Any],
    map_selected_data: Dict[str, Any],
    map_hover_data: Dict[str, Any],
    # States
    current_map_figure: Dict[str, Any],
    current_historic_population_figure: Dict[str, Any],
    prevent_initial_call: bool = True,
) -> Tuple[go.Figure, str]:
    print('---')
    # ================ #
    global gdf
    global pre_filtered_gdf
    global filtered_gdf
    global init
    # ================ #
    
    if ctx.triggered[0]['prop_id'] == 'geojson-precision-radio.value':
        print('---load_data()')
        gdf = load_data(
            precison=geojson_precision,
        )
    
    # Extract the current zoom and center from the figure
    zoom = current_map_figure['layout']['mapbox']['zoom'] if 'mapbox' in current_map_figure['layout'] else 7
    center = current_map_figure['layout']['mapbox']['center'] if 'mapbox' in current_map_figure['layout'] else {"lat": 50.62925, "lon": 3.057256}

    if isinstance(selected_departements, str):
        selected_departements = [selected_departements]
    elif selected_departements is None:
        selected_departements = []
                
    print('ctx.triggered[0]["prop_id"]:', ctx.triggered[0]['prop_id'])
    print('filtering_mode:', filtering_mode)
    if (
        init == True
        or (ctx.triggered[0]['prop_id'] == 'map-graph.relayoutData' and filtering_mode == 'hover-click-mode')
        or ctx.triggered[0]['prop_id'] == 'departement-dropdown.value' 
        or (ctx.triggered[0]['prop_id'] == 'select-all-button.n_clicks' and not filtering_mode == 'windows-filtering-mode')
        or (ctx.triggered[0]['prop_id'] == 'filtering-mode.value' and not filtering_mode == 'windows-filtering-mode')
        or ctx.triggered[0]['prop_id'] == 'geojson-precision-radio.value'
    ):
        print('---deps upload')
        init = False
        pre_filtered_gdf = gdf[gdf['departement'].isin(selected_departements)]
        filtered_gdf = pre_filtered_gdf.copy()
        print(f'len(filtered_gdf): {len(filtered_gdf)}')   
        fig = create_map(
            gdf=filtered_gdf, 
            max_colorscale=max_colorscale,
            colorscale_palette=colorscale_palette,
            marker_opacity=slider_marker_opacity,
            mapbox_style=mapbox_style,
            mapbox_access_token=mapbox_access_token,
        )
        fig.update_layout(mapbox_zoom=zoom, mapbox_center=center, dragmode='zoom',)
        
        print(f'---type(fig): {type(fig)}')
        # if ctx.triggered[0]['prop_id'] == 'filtering-mode.value' and filtering_mode == 'box-select-mode':
        #     fig.update_layout(dragmode='select')
        
        return (
            fig,
            plot_historic_population(
                df_historic_population=df_historic_population,
                codgeo_list=filtered_gdf['codgeo'].tolist()
            ),
            f"Total Population: {filtered_gdf['pop'].sum():,}",
            # f"{', '.join(filtered_gdf['nom'].unique())}"
            ''
        )
        
    if filtering_mode == 'hover-click-mode':
        if map_hover_data:
            codgeo_list = pd.DataFrame(map_hover_data["points"])["customdata"].to_list()
            print('--hover-click-update')
            return (
                current_map_figure,
                plot_historic_population(
                    df_historic_population=df_historic_population,
                    codgeo_list=codgeo_list
                ),
                f"Total Population: {gdf[gdf['codgeo'].isin(codgeo_list)]['pop'].sum():,}",
                # f"{', '.join(filtered_gdf['nom'].unique())}"
                ''
            )
         
        
    if filtering_mode == 'windows-filtering-mode':
        # print('---allo')
        # print(f'map_relayout_data: {map_relayout_data}')
        # print(f'current_map_figure["layout"].keys(): {current_map_figure["layout"].keys()}')
        if (
            ctx.triggered[0]['prop_id'] == 'map-graph.relayoutData' 
            or ctx.triggered[0]['prop_id'] == 'filtering-mode.value'
            ):
            if map_relayout_data and 'mapbox._derived' in map_relayout_data:
                print('---windows-filtering-update')
                lon_min, lat_min = map_relayout_data['mapbox._derived']['coordinates'][3]
                lon_max, lat_max = map_relayout_data['mapbox._derived']['coordinates'][1]
                bounding_box = box(lon_min, lat_min, lon_max, lat_max)
                box_df = gpd.GeoDataFrame(geometry=[bounding_box], crs='EPSG:4326')
                filtered_gdf = gpd.sjoin(pre_filtered_gdf, box_df, how='inner', predicate='within')
                return (
                    create_map(
                        gdf=filtered_gdf, 
                        max_colorscale=max_colorscale,
                        colorscale_palette=colorscale_palette,
                        marker_opacity=slider_marker_opacity,
                        mapbox_style=mapbox_style,
                        mapbox_access_token=mapbox_access_token,
                    ).update_layout(mapbox_zoom=zoom, mapbox_center=center, dragmode='zoom',),
                    plot_historic_population(
                        df_historic_population=df_historic_population,
                        codgeo_list=filtered_gdf['codgeo'].tolist()
                    ),
                    f"Total Population: {filtered_gdf['pop'].sum():,}",
                    # f"{', '.join(filtered_gdf['nom'].unique())}"
                    ''
                )
            

    if filtering_mode == 'box-select-mode':
        
        
        if map_selected_data and ctx.triggered[0]['prop_id'] != 'map-graph.hoverData':
            codgeo_list = pd.DataFrame(map_selected_data["points"])["customdata"].to_list()
            # filtered_gdf = gdf[gdf['codgeo'].isin(codgeo_list)]
            print('--box-select-update')
            return (
                current_map_figure,
                plot_historic_population(
                    df_historic_population=df_historic_population,
                    codgeo_list=codgeo_list
                ),
                f"Total Population: {gdf[gdf['codgeo'].isin(codgeo_list)]['pop'].sum():}",
                # f"{', '.join(filtered_gdf['nom'].unique())}"
                ''
            )
            
        

    total_population = filtered_gdf['pop'].sum()
    metric_text = f"Total Population: {total_population:,}" if selected_departements else "Total Population (All departements):"
    
    if ctx.triggered[0]['prop_id'] == 'mapbox-style-radio.value':
        print('---map-style-update')
        return (
            current_map_figure.update_layout(mapbox_style=mapbox_style),
            current_historic_population_figure,
            metric_text,
            ''
        )
        
    print(f'---bottom-update')
    return (
        current_map_figure,
        current_historic_population_figure,
        metric_text, 
        ''
    )

    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
