import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_map(
    df: pd.DataFrame,
    color_mode: str = 'motiontype',
    zoom_init: float = 13,
    zoom_m: float = 20,
    height: int = 400,
) -> px.scatter_mapbox:
 
    df = df.copy()
    if 'motiontype' in df.columns:
        df['motiontype'] = df['motiontype'].astype(str)
    if 'mode' in df.columns:
        df['mode'] = df['mode'].astype(str)
    if 'phoneconfigurationid' in df.columns:
        df['phoneconfigurationid'] = df['phoneconfigurationid'].astype(str)
    if color_mode == 'motiontype':
        color_discrete_map = {
            '-1.0': 'skyblue',
            '0.0': 'green',
            '1.0': 'red',
            '3.0': 'orange',
            '7.0': 'purple',
            
            '-1': 'skyblue',
            '0': 'green',
            '1': 'red',
            '3': 'orange',
            '7': 'purple',
        }
    elif color_mode == 'phoneconfigurationid':
        color_discrete_map = None
    elif color_mode == 'mode':
        color_discrete_map = {
            '0': 'white',
            '1': 'green',
            '8': 'red',
            '13': 'blue',
            '4': 'yellow',
            '11': 'pink',
            '67': 'pink',
            '999': 'pink',
            '6' : 'pink',
        }
    
    # Calculate the center of the map
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Calculate the zoom level, exclude outliers
    lat_range = df['latitude'].quantile(0.95) - df['latitude'].quantile(0.05)
    lon_range = df['longitude'].quantile(0.95) - df['longitude'].quantile(0.05)
    zoom = zoom_init - max(lat_range, lon_range) * zoom_m  # Adjust the multiplier as needed
    
    # Add text info for each point
    df['text'] = df['datetime'].dt.strftime('%H:%M')
    
    fig = px.scatter_mapbox(
        df, 
        lat='latitude', 
        lon='longitude', 
        hover_data=df.columns,
        color=color_mode,
        color_discrete_map=color_discrete_map,
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        template='plotly_dark',
        text='text'  # Add text to display on the map
    )      
    
    fig.update_layout(
        title=dict(
            text=f"Records {df['userid'].iloc[0]} on {df['datetime'].dt.date.iloc[0]}"
                 f"<br>os"
                 f"<br>-",
            x=0.05,
            y=0.95,
            xanchor='left',
            yanchor='top',
            font=dict(size=12)
        ),
        showlegend=True,
        mapbox_style='carto-darkmatter',
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            title=color_mode,
            orientation='h',
            yanchor='bottom',
            xanchor='right',
            x=.95,
            y=0,
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"text": [None]}],
                        label="-",
                        method="restyle",
                    ),
                    dict(
                        args=[{"text": [df['text']]}],
                        label="hh:mm",
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=False,
                active=0,
                x=0,
                xanchor="left",
                y=0,
                yanchor="bottom",
                bgcolor='#333333',
                bordercolor='white',
                font=dict(color='white'),
                
            ),
        ],
        height=height,
    )
    return fig

def plot_timeline(
    df: pd.DataFrame,
    height: int = 250,
    color_mode: str = 'motiontype',
) -> go.Figure:
    if df.empty:
        return go.Figure(go.Scatter(), layout=dict(title="No data available"))
    
    df = df.copy()
    if 'motiontype' in df.columns:
        df['motiontype'] = df['motiontype'].astype(str)
    if 'mode' in df.columns:
        df['mode'] = df['mode'].astype(str)
    if 'phoneconfigurationid' in df.columns:
        df['phoneconfigurationid'] = df['phoneconfigurationid'].astype(str)
    
    if color_mode == 'motiontype':
        color_discrete_map = {
            "-1.0": 'skyblue',
            "0.0": 'green',
            "1.0": 'red',
            "3.0": 'orange',
            "7.0": 'purple',
                    
            '-1': 'skyblue',
            '0': 'green',
            '1': 'red',
            '3': 'orange',
            '7': 'purple',
        }
    elif color_mode == 'phoneconfigurationid':
        color_discrete_map = None
    elif color_mode == 'mode':
        color_discrete_map = {
            '0': 'white',
            '1': 'green',
            '8': 'red',
            '13': 'blue',
            '4': 'yellow',
            '11': 'pink',
            '67': 'pink',
            '999': 'pink',
            '6' : 'pink',
        }
    
    fig = go.Figure()

    # Add speed scatter plot - Motion Type
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['speed'],
            mode='markers',
            marker=dict(color=df[color_mode].map(color_discrete_map), size=5),
            name='Speed',
            hoverinfo='text',
            hovertext=df.apply(lambda row: f"Time: {row['datetime']}"
                                           f"<br>Speed: {round(row['speed'], 1)}"
                                           f"<br>speed_calc: {round(row['speed_calc'], 1)}"
                                           f"<br>Motion Type: {row['motiontype']}"
                                        #    f"<br>Mode: {row['mode']}"
                                        #    f"<br>Segment: {row['segment']}"
                                        #    f"<br>os: {row['os']}"
                                           f"<br>Altitude: {round(row['altitude'], 1)}"
                                , axis=1),
            showlegend=True,
            visible = True,
        )
    )
    
    # speed_calc trace
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['speed_calc'],
            mode='markers',
            marker=dict(color=df[color_mode].map(color_discrete_map), size=5),
            # line=dict(color='blue', width=1),
            name='Speed_calc',
            hoverinfo='text',
            hovertext=df.apply(lambda row: f"Time: {row['datetime']}"
                                           f"<br>Speed: {round(row['speed'], 1)}"
                                           f"<br>Speed_calc: {round(row['speed_calc'], 1)}"
                                           f"<br>Motion Type: {row['motiontype']}"
                                        #    f"<br>Mode: {row['mode']}"
                                        #    f"<br>Segment: {row['segment']}"
                                        #    f"<br>os: {row['os']}"
                                           f"<br>Altitude: {round(row['altitude'], 1)}"
                                , axis=1),
            showlegend=True,
            visible='legendonly',
        )
    )
    
    # Add altitude trace
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['altitude'],
            yaxis='y2',
            mode='lines',
            line=dict(color='yellow', width=1),
            name='Altitude',
            hoverinfo='text',
            hovertext=df.apply(lambda row: f"Time: {row['datetime']}"
                                        #    f"<br>Speed: {round(row['speed'], 1)}"
                                        #    f"<br>Speed_calc: {round(row['speed_calc'], 1)}"
                                        #    f"<br>Motion Type: {row['motiontype']}"
                                        #    f"<br>Mode: {row['mode']}"
                                        #    f"<br>Segment: {row['segment']}"
                                        #    f"<br>os: {row['os']}"
                                           f"<br>Altitude: {round(row['altitude'], 1)}"
                                , axis=1),
            showlegend=True,
            visible='legendonly',
        )
    )
        
        
    fig.update_layout(
        yaxis1=dict(
            title='Speed (km/h)',
            range=[0, min(df['speed'].max() + 20, 150)],
        ),
        
        yaxis2=dict(
            title='Altitude (m)',
            overlaying='y',
            side='right',
            showgrid=False,
            # showzeroline=False,
        ),
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            title="Traces:",
            x=0,
            y=1,
            xanchor='left',
            yanchor='bottom',
            orientation='h',
            
        ),
        height=height,
    )
    return fig
