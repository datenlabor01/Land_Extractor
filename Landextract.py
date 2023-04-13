import plotly.express as px
import pandas as pd
pd.options.mode.chained_assignment = None
from dash import Dash, html, dcc, Input, Output, dash_table, State
import dash_bootstrap_components as dbc

df_data = pd.read_csv("https://raw.githubusercontent.com/datenlabor01/Land_Extractor/main/gv_data.csv")
app = Dash(external_stylesheets = [dbc.themes.LUX])

#Dropdown for indicator:
project_select = dcc.Dropdown(options=sorted(df_data["BMZ Nummer"].unique()),
                             value='All', style={"textAlign": "center"}, clearable=False, multi=True, placeholder='Projektnummer auswählen')

value_select = dcc.Dropdown(options=["Auftragsbetrag gesamt BMZ-Mittel", "Auszahlungsbetrag gesamt",
                                     "Geplante Beauftragungen 2023"],
                             value='All', style={"textAlign": "center"}, clearable=False, multi=False, placeholder='Messgröße auswählen (Default: Auftragsbetrag BMZ-Mittel)')

country_select = dcc.Dropdown(options=sorted(df_data["Country"].unique()),
                             value='All', style={"textAlign": "center"}, clearable=False, multi=True, placeholder='Land auswählen')

text2 = "Diese Anwendung wird als Prototyp vom BMZ Datenlabor angeboten. Sie kann Fehler enthalten und ist als alleinige Entscheidungsgrundlage nicht geeignet. Außerdem können Prototypen ausfallen oder kurzfristig von uns verändert werden. Sichern Sie daher wichtige Ergebnisse per Screenshot oder Export. Die Anwendung ist vorerst intern und sollte daher nicht ohne Freigabe geteilt werden. Wenden Sie sich bei Fragen gerne an datenlabor@bmz.bund.de"

app.layout = dbc.Container([
      dbc.Row([
         html.Div(html.Img(src="https://github.com/datenlabor01/LS/raw/main/logo.png", style={'height':'80%', 'width':'20%'})),
         html.H1(children='Prototyp Länderüberblick'),
         html.P(children = "Das ist ein Prototyp, der Fehler enthalten kann.")],
         style={'textAlign': 'center'}),

      dbc.Row([
         dbc.Button(children = "Über diese App", id = "textbutton", color = "light", className = "me-1",
                    n_clicks=0, style={'textAlign': 'center', "width": "30rem"})
      ], justify = "center"),
      dbc.Row([
            dbc.Collapse(dbc.Card(dbc.CardBody([
               dbc.Badge(text2, className="text-wrap"),
               ])), id="collapse", style={'textAlign': 'center', "width": "60rem"}, is_open=False),
      ], justify = "center"),

      dbc.Row([
        dbc.Col([project_select, html.Br(), value_select], width = 8),
      ], justify = "center"),

      dbc.Row([
         dcc.Graph(id='map', style={'textAlign': 'center'}),
      ]),

      dbc.Row([
        dbc.Col([
         dcc.Dropdown(id="country_dd", placeholder='Alle Länder', value = "All",
         style = {"textAlign": "center"}, clearable=True, multi=True), html.Br()], width = 8),
      ], justify = "center"),

      #Data Table:
      dbc.Row([
         my_table := dash_table.DataTable(
         df_data.to_dict('records'), [{"name": i, "id": i} for i in df_data.columns],
         filter_action="native", sort_action="native", page_size= 25,
         style_cell={'textAlign': 'left', "whiteSpace": "normal", "height": "auto"},
         style_header={'backgroundColor': 'rgb(11, 148, 153)', 'color': 'black', 'fontWeight': 'bold'},
             style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(235, 240, 240)',
        }], export_format= "xlsx"),
         ]),
])

#Button to display text:
@app.callback(
    Output("collapse", "is_open"),
    [Input("textbutton", "n_clicks")],
    [State("collapse", "is_open")],
)

def collapse(n, is_open):
   if n:
      return not is_open
   return is_open

#Funktion um nur Länder anzuzeigen, die in gewählter Kategorie sind:
@app.callback(
    Output("country_dd", "options"),
    Input(project_select, 'value'),
    )

def country_options(project_select ):
    if (project_select == "All") | (project_select == []):
      return sorted(df_data['Country'].unique())
    else:
      df_temp = df_data[df_data["BMZ Nummer"].isin(project_select)]
      return sorted(df_temp['Country'].unique())

@app.callback(
    [Output('map', 'figure'), Output(my_table, "data"), Output(my_table, "columns")],
    [Input(project_select, 'value'), Input(value_select, 'value'), Input("country_dd", 'value')]
)

def update_map(project_select, value_select, country_select):

   if (project_select == "All") | (project_select == []):
      dat_map = df_data
   else:
      dat_map = df_data[df_data["BMZ Nummer"].isin(project_select)]

   if (value_select == "All") | (value_select == "Auftragsbetrag gesamt BMZ-Mittel"):
      dat_map["Value"]  = dat_map["Auftragsbetrag gesamt BMZ-Mittel"]
   if value_select == "Auszahlungsbetrag gesamt":
      dat_map["Value"] = dat_map["Auszahlungsbetrag gesamt"]
   if value_select == "Geplante Beauftragungen 2023":
      dat_map["Value"] = dat_map["Geplante Beauftragungen 2023"]

   dat = dat_map.groupby(["Land", "Country"])["Value"].sum().reset_index()

   figMap = px.choropleth(dat, locations = "Land", locationmode="ISO-3", hover_data= ["Country"],
                        color_continuous_scale="Fall", color= "Value")
   figMap.update(layout_coloraxis_showscale = False)

   if (country_select == "All") | (country_select == []):
      dat_table = dat_map
   else:
      dat_table = dat_map[dat_map["Country"].isin(country_select)]

   dat_table = dat_table.drop_duplicates(subset=["BMZ Nummer"])

   return figMap, dat_table.to_dict("records"), [{"name": i, "id": i} for i in dat_table.columns[3:-1]]

if __name__ == '__main__':
    app.run_server(debug=True)