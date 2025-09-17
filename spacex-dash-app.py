# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
# TASK 1: Prepare dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([dcc.Dropdown(id='site-dropdown',options=dropdown_options,value='ALL',placeholder="Select a Launch Site here",searchable=True)]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000,marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'}, value=[min_payload, max_payload]),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# TASK 2: Callback for success pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Use all rows: show total successful launches per site
        fig = px.pie(
            spacex_df, 
            names='Launch Site',       # show counts per launch site
            values='class',            # total success counts
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success vs. failure
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']  # rename columns for px.pie
        fig = px.pie(
            success_counts, 
            names='class',             # 0 = Failure, 1 = Success
            values='count', 
            title=f'Success vs. Failure for site {entered_site}'
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4: Callback for success-payload scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter by payload range first
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
        return fig
    else:
        # Further filter by selected launch site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {entered_site}'
        )
        return fig


# Run the app
if __name__ == '__main__':
    app.run()
