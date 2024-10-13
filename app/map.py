import geopandas as gpd
import plotly.graph_objects as go

def create_map(
    gdf: gpd.GeoDataFrame,
) -> go.Figure:
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
            showscale=True,
            colorbar=dict(
                title='Population',
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                tickfont=dict(color='white'),
                titlefont=dict(color='white'),
                x=0,
                y=1,
                xpad=20,
                # ypad=0,
                xanchor='left',
                yanchor='top',
                len=0.5,
            ),
        )
    )

    # Set up the map layout
    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_zoom=7,
        # center to Lille
        mapbox_center={"lat": 50.62925, "lon": 3.057256},
        margin={"r":0,"t":0,"l":0,"b":0},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
    )
    
    return fig_map