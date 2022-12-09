import pandas as pd
import plotly.express as px
import dash
import os
from datetime import datetime


# ------------------ PATHs -------------------
currentPath = os.path.dirname(os.path.abspath(__file__))
STOCK_DATA = currentPath + '/data/stock'
COMPANY_CODES = currentPath + '/data/HighVolatilityCompanies.csv'
# --------------------------------------------

def getLastCsv(dataPath):
    csvs = [file.split('.')[0] for file in os.listdir(dataPath) if file.split('.')[-1] == 'csv']
    csvs = [datetime.strptime(date, '%Y-%m-%d').date() for date in csvs]
    csvs.sort()
    last_csv = str(csvs[-1])

    last_csv_path = dataPath +'/' + str(csvs[-1]) + '.csv'

    return last_csv_path

def get_2022_data(path):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
    columns = ['date', 'company', 'open', 'high', 'low', 'close', 'adjusted_close']
    df = df[columns]
    df['daily_%_var'] = (df['adjusted_close'] - df['open']) / df['open']
    df['mean'] = (df['open'] + df['adjusted_close']) / 2
    df['intraDaily_%_var'] = (df['high'] - df['low']) / df['mean']
    df = df.loc[df['date'].dt.year == 2022]
    return df

def getDropDownValues(path):
    df = pd.read_csv(path)

    list_of_dict = []

    for row in range(df.shape[0]):
        value = df.iloc[row,0]
        label = df.iloc[row,1]
        
        temp_dict = {}
        temp_dict['value'] = value
        temp_dict['label'] = label
        list_of_dict.append(temp_dict)

    return list_of_dict

lastCsvPath = getLastCsv(STOCK_DATA)


app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = dash.html.Div(children=[dash.html.H1('HIGH VOLATILITY STOCK COMPANIES IN 2022',
                                                  style={'textAlign':'center'}),
                                     dash.dcc.Dropdown(id='dropDown1',
                                                       options=getDropDownValues(COMPANY_CODES)),
                                     dash.html.Div([dash.html.Div([ ],
                                                                 id='meanPlot'),
                                                    dash.html.Div([ ],
                                                                 id='varPlot')
                                                   ],
                                                   style={'display':'flex'}
                                                  ),
                                     dash.html.Div(dash.html.Div([ ],id='intraVarPlot')
                                                  )
                                     ]
                          )


@app.callback([dash.dependencies.Output(component_id='varPlot',component_property='children'),
               dash.dependencies.Output(component_id='meanPlot', component_property='children'),
               dash.dependencies.Output(component_id='intraVarPlot',component_property='children')],
              dash.dependencies.Input(component_id='dropDown1', component_property='value'))
def get_plot(value):
    df = get_2022_data(lastCsvPath)
    df_plot = df.loc[df['company'] == value]

    fig_mean = px.line(data_frame=df_plot, x='date', y='mean', width=700, height=300)
    fig_mean.update_layout(title='Average daily stock value', title_x=0.5)

    fig_var = px.line(data_frame=df_plot, x='date', y='daily_%_var', width=700, height=300) 
    fig_var.update_layout(title='Daily % variation', title_x=0.5)
    fig_var.update_traces(line_color="green")

    fig_intraVar = px.line(data_frame=df_plot, x='date', y='intraDaily_%_var', width=700, height=300)
    fig_intraVar.update_layout(title='Intra Daily % variation', title_x=0.5)
    fig_intraVar.update_traces(line_color='red')

    return [dash.dcc.Graph(figure=fig_var),
            dash.dcc.Graph(figure=fig_mean),
            dash.dcc.Graph(figure=fig_intraVar)]

if __name__ == '__main__':
    app.run_server()