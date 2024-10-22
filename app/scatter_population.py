import plotly.graph_objects as go
import pandas as pd
from typing import List

def plot_historic_population(
    df_historic_population: pd.DataFrame,
    codgeo_list: List[str] = None,
    codgeo: str = None,
    departements_list: List[str] = None,
) -> go.Figure:
    
    if (not codgeo_list and not codgeo
        or codgeo_list and codgeo) and not departements_list:
        raise ValueError('You must provide `codgeo_list` or `codgeo` or `departements_list`')
    
    # check if codgeo is list or not
    if isinstance(codgeo, str):
        codgeo_list = [codgeo]
    
    # Filter and transpose the DataFrame
    if departements_list:
        df = df_historic_population[df_historic_population['departement'].isin(departements_list)]
        print(f'df.head(): {df.head()}')
    else:
        df = df_historic_population[df_historic_population['codgeo'].isin(codgeo_list)]
    df = df.T[4:]
    df['population'] = df.sum(axis=1)
    df.reset_index(inplace=True)
    df.rename(columns={'index':'year'}, inplace=True)
    df = df[['year','population']].reset_index(drop=True)

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
            # text=f'{nom}',
            x=.95,
            y=0.95,
            xanchor='right',
            yanchor='top',
        ),
        yaxis_title='Population',
        xaxis=dict(type='date'),
        template='plotly_white',
        margin={"r":0,"t":0,"l":0,"b":0},
        # height=200
    )

    return fig
