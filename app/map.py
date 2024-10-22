import geopandas as gpd
import plotly.graph_objects as go

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
                bgcolor='white',
                bordercolor='white',
                # bgcolor='rgba(0,0,0,0)',
                # bordercolor='rgba(0,0,0,0)',
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
