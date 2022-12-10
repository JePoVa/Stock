import pandas as pd
import plotly.express as px
import dash
import os
from datetime import datetime, date
import seaborn as sns


# ------------------ INPUTS -------------------
currentPath = os.path.dirname(os.path.abspath(__file__))
STOCK_DATA = currentPath + '/data/stock'
COMPANY_CODES = currentPath + '/data/HighVolatilityCompanies.csv'
YEAR = 2022
# --------------------------------------------

def getLastCsv(dataPath):
    csvs = [file.split('.')[0] for file in os.listdir(dataPath) if file.split('.')[-1] == 'csv']
    csvs = [datetime.strptime(date, '%Y-%m-%d').date() for date in csvs]
    csvs.sort()
    last_csv = str(csvs[-1])

    last_csv_path = dataPath +'/' + str(csvs[-1]) + '.csv'

    return last_csv_path

def get_yearly_data(path):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
    columns = ['date', 'company', 'open', 'high', 'low', 'close', 'adjusted_close']
    df = df[columns]
    df['mean'] = (df['open'] + df['adjusted_close']) / 2
    df['intraDaily_%_var'] = (df['high'] - df['low']) / df['mean']
    df = df.loc[df['date'].dt.year == YEAR]
    return df

def getDropDownValues(path):
    df = pd.read_csv(path)

    list_of_dict = []

    for row in range(df.shape[0]):
        value = df.iloc[row,0]
        label = df.iloc[row,1] + '  (' + df.iloc[row,0] + ')'
        
        temp_dict = {}
        temp_dict['value'] = value
        temp_dict['label'] = label
        list_of_dict.append(temp_dict)

    return list_of_dict

lastCsvPath = getLastCsv(STOCK_DATA)


app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = dash.html.Div(children=[dash.html.H1(f'HIGH VOLATILITY STOCK COMPANIES IN {YEAR}',
                                                  style={'textAlign':'center'}),
                                     dash.html.H3('This is a subtitle',
                                                  style={'textAlign':'center'}),
                                     dash.dcc.Dropdown(id='dropDown1',
                                                       options=getDropDownValues(COMPANY_CODES)),
                                     dash.html.Div([dash.html.Div([ ],
                                                                 id='meanPlot'),
                                                    dash.html.Div([ ],
                                                                 id='intraVarPlot')
                                                   ],
                                                   style={'display':'flex'}
                                                  ),
                                     #dash.html.Div([dash.html.Div([ ],
                                     #                             id='intraVarPlot_DEPRECATED'),
                                     #               dash.html.Div([ ],
                                     #                             id='openDensity')
                                     #              ]                                                 
                                     #             ),
                                     dash.html.Div([dash.dcc.DatePickerRange(id='datesPicker',
                                                                            min_date_allowed=f'{YEAR}-01-01',
                                                                            max_date_allowed=f'{YEAR}-12-31',
                                                                            display_format='DD-MM-YYYY'
                                                                            ),
                                                    dash.html.Div([ ],
                                                                  id='zoomPlot')  
                                                   ]
                                                  )
                                     ]
                          )


@app.callback([dash.dependencies.Output(component_id='meanPlot', component_property='children'),
                    dash.dependencies.Output(component_id='intraVarPlot',component_property='children'),
                    dash.dependencies.Output(component_id='zoomPlot', component_property='children')],
              [dash.dependencies.Input(component_id='dropDown1', component_property='value'),
                    dash.dependencies.Input(component_id='datesPicker', component_property='start_date'),
                    dash.dependencies.Input(component_id='datesPicker', component_property='end_date')])
def get_plot(value, start_date, end_date):
    # ------ Creating data_frames and variables for later plotting ------
    df = get_yearly_data(lastCsvPath)
    df_plot = df.loc[df['company'] == value]
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    df_plot_dates = df_plot.loc[(df_plot['date'] > start_date) & (df_plot['date'] < end_date)]

    # ------ mean plot ------
    fig_mean = px.line(data_frame=df_plot, x='date', y='mean', width=700, height=300)
    fig_mean.update_layout(title='Average daily stock value', title_x=0.5)

    # ------ intra daily var plot ------
    fig_intraVar = px.line(data_frame=df_plot, x='date', y='intraDaily_%_var', width=700, height=300,
                           labels={'intraDaily_%_var':'Intra-daily % variation'})
    fig_intraVar.update_layout(title='Intra Daily % variation', title_x=0.5)
    fig_intraVar.update_traces(line_color='red')

    # ------ zoom plot ------
    fig_zoom = px.line(data_frame=df_plot_dates, x='date', y='mean', width=700, height=300)
    fig_zoom.update_layout(title='Open value for selected dates', title_x=0.5)
    fig_zoom.update_traces(line_color='green')
    

    return [dash.dcc.Graph(figure=fig_mean),
            dash.dcc.Graph(figure=fig_intraVar),
            dash.dcc.Graph(figure=fig_zoom)]

if __name__ == '__main__':
    app.run_server()