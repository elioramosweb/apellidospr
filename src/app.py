import dash_bootstrap_components as dbc
from dash import html,dcc,Output,Input 
from shapely.geometry import Polygon, Point
import plotly.express as px
import pandas as pd 
import numpy as np 
import dash
import json
import random


app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}
               ],
)

# suppress_callback_exceptions = True

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

server = app.server

# diccionario con la poblacion por municipio

poblacion = np.load('poblacion.npy', allow_pickle='TRUE').item()


# tabla de contingencia de conteo de apellidos por municipip

tabla = pd.read_pickle("tabla.pkl")

# mapa de geojson

f = open('municipalities.geojson')

mapaMunicipios = json.load(f)

# cambiar los nombres de los municipios a mayúsculas y quitarle los acentos

rep = str.maketrans('ÁÉÍÓÚÜ', 'AEIOUU')

for inx in range(78):
    temp = mapaMunicipios["features"][inx]["properties"]["NAME"]
    mapaMunicipios["features"][inx]["properties"]["NAME"] = \
        temp.upper().translate(rep)


mapaMunicipiosReverse = json.load(open("municipios.geojson"))


# función para generar puntos aleatorios dentro de un poligono en el mapa

def random_points_within(poly, num_points):

    min_x, min_y, max_x, max_y = poly.bounds

    points = []
    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x),
                              random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points


buscador = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Label("Entre apelllido:",style={'font-weight': 'bold'}),
                dbc.Input(id="input_apellido",
                          type="text",
                          value="RIVERA",
                          debounce=True),
            ]
        ),

        dbc.FormGroup(
            [
                html.P("No incluya acentos y puede utilizar letras \
                       mayúsculas o minúsculas",
                       style={'align': 'left',
                              'font-weight': 'bold',
                              'color': '#2fa4e7'})
            ]
        ),

    ],
    body=True,
)


seleccionador = dbc.Card(
    [

        dbc.FormGroup(
            [
                dbc.Label("Método de Visualización",style={'font-weight': 'bold'}),
                dcc.Dropdown(
                    id="input_seleccion",
                    options=[
                        {"label": "Gráfico de Barras", "value": "Barras"},
                        {"label": "Mapa Coroplético", "value": "Coroplético"},
                        {"label": "Mapa de Densidades", "value": "Densidad"}
                    ],
                    value="Barras",
                ),
            ],
        ),


        # html.Br(),

        dbc.FormGroup(
            [

                html.Div(id="slider_container", children=[

                    dbc.Label("Cantidad de municipios"),
                    dcc.Slider(1, 78, 10,
                        value=10,
                        id="input_slider",
                    ),
                    html.Div(id="output_slider", style={'display': 'block'}),
                ]),

            ]),



        dbc.FormGroup(
            [
                html.Br(),
                html.Div(id="creditos", children=[
                    html.P("apellidospr es un proyecto del grupo CienciaDatosPR del  \
                            Departamento de Matemáticas de \
                            la Universidad de Puerto Rico \
                            en Humacao.", style={'align': 'justify',
                                                 'font-weight': 'bold',
                                                 'color':'#2fa4e7'})
                ],
                         ),
            ],
        ),


       ], body=True,



)


creditos = dbc.Card(
    [
        html.Div(id="creditos", children=[
                html.P("apellidospr es un proyecto del grupo CienciaDatosPR del  \
                        Departamento de Matemáticas de \
                        la Universidad de Puerto Rico \
                        en Humacao.", style={'align': 'justify'})
        ],),


    ],
    body=True, style={'border-radius': '10px',
                      'align': 'top',
                      'height': '200px'},
)

estadisticas = dbc.Card(

        dbc.FormGroup(
            [
                html.Br(),
                html.Div(id='titulo',style={'font-weight': 'bold'}),
                html.Div(id="rank"),
                html.Div(id="cantidad"),
                html.Div(id="frecuencia"),
                html.Br(),
              ], style={'textAlign': 'center'}),
)

similares = dbc.Card(
        dbc.FormGroup(
            [
                html.Br(),
                html.Div(id="similares"),
                html.Br(),
            ], style={'textAlign': 'center', 'border-radius': '10px','font-weight': 'bold'}),
)


app.layout = dbc.Container(
    [
        html.H1("ApellidosPR"),
        html.H3("Una aplicación para el análisis y \
                visualización de los apellidos en Puerto Rico"),
        html.Br(),
        html.Hr(),


        dbc.Row(
            [
                dbc.Col(buscador, align="top", md=4),
                dbc.Col(estadisticas, align="top", md=8),
            ],
        ),


        dbc.Row(
            [
                dbc.Col(seleccionador, align="top", md=4),
                dbc.Col(dcc.Graph(id="visualizacion"), md=8),
            ],
        ),


        dbc.Row(
            [
                dbc.Col(" ", align="top", md=4),
                dbc.Col(similares, align="top", md=8),
            ],
        ),



    ], fluid=True,
)


@app.callback(
   Output(component_id='slider_container', component_property='style'),
   [
       Input(component_id='input_seleccion', component_property='value'),
   ])
def show_slider(miSeleccion):
    if miSeleccion == 'Barras':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    dash.dependencies.Output('output_slider', 'children'),
    [dash.dependencies.Input('input_slider', 'value')])
def update_output(value):
    return 'Cantidad de municipios: {}'.format(value)


@app.callback(
    Output("visualizacion", "figure"),
    [
        Input(component_id='input_seleccion', component_property='value'),
        Input(component_id='input_apellido', component_property='value'),
        Input(component_id='input_slider', component_property='value')
    ],
)
def update_metodo(miSeleccion, miApellido, cantidadMunicipios):
    if miSeleccion == "Barras":
        fig = graficoBarras(cantidadMunicipios, miApellido.upper())
    elif miSeleccion == "Coroplético":
        fig = mapaCoropletico(mapaMunicipios, miApellido.upper())
    elif miSeleccion == "Densidad":
        fig = mapaDensidad(mapaMunicipiosReverse, miApellido.upper())
    else:
        fig = graficoBarras(cantidadMunicipios, miApellido.upper())

    return fig


@app.callback(
    Output("titulo", "children"),
    [
        Input(component_id='input_apellido', component_property='value')
    ],
)
def update_output_div(miApellido):
    return 'Análisis del apellido {}'.format(miApellido.upper())


@app.callback(
    Output("rank", "children"),
    [
        Input(component_id='input_apellido', component_property='value')
    ],
)
def update_rank(miApellido):
    return rank(miApellido.upper())


@app.callback(
    Output("frecuencia", "children"),
    [
        Input(component_id='input_apellido', component_property='value')
    ],
)
def update_frecuencia(miApellido):
    return frecuencia(miApellido.upper())


@app.callback(
    Output("cantidad", "children"),
    [
        Input(component_id='input_apellido', component_property='value')
    ],
)
def update_cantidad(miApellido):
    return cantidad(miApellido.upper())


@app.callback(
    Output("similares", "children"),
    [
        Input(component_id='input_apellido', component_property='value')
    ],
)
def update_similares(miApellido):
    return similares(miApellido.upper())


def graficoBarras(cantidadMunicipios, miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        # conteo de apellidos por municipio

        conteo = {}

        for municipio in list(poblacion.keys()):
            conteo[municipio] = tabla[miApellido][municipio]

        # porciento de apellidos por municipio (normalizados por la población)

        porciento = {}

        for muni in list(poblacion.keys()):
            porciento[muni] = round(100*conteo[muni]/poblacion[muni], 2)

        top = sorted(porciento.items(), key=lambda x: x[1], reverse=True)[0:78]

        municipioSort = []
        porcientoSort = []

        for key, value in top:
            municipioSort.append(key)
            porcientoSort.append(float(value))

        data = pd.DataFrame([municipioSort, porcientoSort]).transpose()

        data.columns = ["municipio", "frecuencia"]

        fig = px.bar(data[0:cantidadMunicipios],
                     x="frecuencia",
                     y="municipio",
                     height=600,
                     color="municipio",
                     orientation="h")

        fig.update_layout(margin=dict(l=10, r=10, b=20, t=1))

        fig.update_layout(showlegend=False)

        return fig

    else:

        temp = graficoBarras_vacio(miApellido)

        return temp


def graficoBarras_vacio(miApellido):

    miApellido = miApellido.upper()

    data = pd.DataFrame([list(range(78)), [0]*78]).transpose()

    data.columns = ["municipio", "frecuencia"]

    fig = px.bar(data[0:9],
                 x="frecuencia",
                 y="municipio",
                 color="municipio",
                 width=800,
                 height=400,
                 orientation="h")

    fig.update_layout(margin=dict(l=10, r=10, b=10, t=10))

    mensaje = "Apellido " + str(miApellido) + " NO disponible"

    fig.add_annotation(text=mensaje,
                       font=dict(family="Open sans", size=34, color="#000000"),
                       x=0, y=4, showarrow=False)

    fig.update_layout(margin=dict(l=10, r=10, b=10, t=1))

    return fig


def mapaTematico(mapaMunicipios, miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        # conteo de apellidos por municipio

        conteo = {}

        for municipio in list(poblacion.keys()):
            conteo[municipio] = tabla[miApellido][municipio]

        # porciento de apellidos por municipio (normalizados por la población)

        porciento = {}

        for muni in list(poblacion.keys()):
            porciento[muni] = round(100*conteo[muni]/poblacion[muni], 2)

        top = sorted(porciento.items(), key=lambda x: x[1], reverse=True)[0:78]

        municipioSort = []
        porcientoSort = []

        for key, value in top:
            municipioSort.append(key)
            porcientoSort.append(float(value))

        minFrec = min(porcientoSort)
        maxFrec = max(porcientoSort)

        data = pd.DataFrame([municipioSort, porcientoSort]).transpose()

        data.columns = ["municipio", "frecuencia"]

        data["frecuencia"] = pd.to_numeric(data["frecuencia"])

        fig = px.choropleth(data, geojson=mapaMunicipios,
                            locations="municipio",
                            color='frecuencia',
                            color_continuous_scale="Reds",
                            range_color=(minFrec, maxFrec),
                            featureidkey="properties.NAME")

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(l=10, r=10, b=10, t=1))
        fig.update_layout(showlegend=False)

        return fig

    else:

        temp = mapaTematico_vacio(mapaMunicipios, miApellido)

        return temp


def mapaTematico_vacio(mapaMunicipios, miApellido):

    miApellido = miApellido.upper()

    # conteo de apellidos por municipio

    conteo = {}

    for municipio in list(poblacion.keys()):
        conteo[municipio] = 0.0

    # porciento de apellidos por municipio (normalizados por la población)

    porciento = {}

    for muni in list(poblacion.keys()):
        porciento[muni] = round(100*conteo[muni]/poblacion[muni], 2)

    top = sorted(porciento.items(), key=lambda x: x[1], reverse=True)[0:78]

    municipioSort = []
    porcientoSort = []

    for key, value in top:
        municipioSort.append(key)
        porcientoSort.append(0)

    minFrec = 0.0
    maxFrec = 0.0

    data = pd.DataFrame([municipioSort, porcientoSort]).transpose()

    data.columns = ["municipio", "frecuencia"]

    data["frecuencia"] = pd.to_numeric(data["frecuencia"])

    fig = px.choropleth(data, geojson=mapaMunicipios, locations="municipio",
                        color='frecuencia', color_continuous_scale="Reds",
                        range_color=(minFrec, maxFrec),
                        featureidkey="properties.NAME")

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=10, r=10, b=10, t=1))
    fig.update_layout(showlegend=False)

    return fig


def mapaDensidad(mapaMunicipiosR, miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        randPos = []

        for inx in range(78):

            poly = Polygon(mapaMunicipiosReverse["features"][inx]
                           ["geometry"]["coordinates"][0])

            muniT = mapaMunicipiosR["features"][inx]["properties"]["NAME"]

            minConteo = min(tabla[miApellido])
            maxConteo = max(tabla[miApellido])

            conteo = 500*(tabla[miApellido][muniT] -
                          minConteo)/(maxConteo - minConteo)
            frec = 500*(conteo/poblacion[muniT])

            points = random_points_within(poly, conteo)

            for p in points:
                randPos.append([muniT, p.x, p.y, frec])

        data = pd.DataFrame(randPos)

        data.columns = ["municipio", "latitude", "longitude", "frecuencia"]

        fig = px.density_mapbox(lat=data.latitude,
                                lon=data.longitude,
                                z=data.frecuencia,
                                hover_name=data.municipio,
                                center=dict(lat=18.25178, lon=-66.264513),
                                zoom=8,
                                mapbox_style="stamen-terrain",
                                radius=5)

        fig.update_layout(margin=dict(l=10, r=10, b=10, t=1))

        fig.update_layout(showlegend=False)

        return fig

    else:

        temp = mapaDensidad_vacio(mapaMunicipiosReverse, miApellido)

        return temp


def mapaDensidad_vacio(mapaMunicipiosR, miApellido):

    randPos = []

    for inx in range(78):

        poly = Polygon(mapaMunicipiosR["features"][inx]
                       ["geometry"]["coordinates"][0])

        muniT = mapaMunicipiosR["features"][inx]["properties"]["NAME"]

        frec = 0

        points = random_points_within(poly, 1)

        for p in points:
            randPos.append([muniT, p.x, p.y, frec])

    data = pd.DataFrame(randPos)

    data.columns = ["municipio", "latitude", "longitude", "frecuencia"]

    fig = px.density_mapbox(lat=data.latitude,
                            lon=data.longitude,
                            z=data.frecuencia,
                            hover_name=data.municipio,
                            center=dict(lat=18.25178, lon=-66.264513), zoom=8,
                            mapbox_style="stamen-terrain",
                            radius=1)

    fig.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 1})

    fig.update_layout(showlegend=False)

    return fig


def mapaCoropletico(mapaMunicipios, miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        listaMunicipio = list(tabla[miApellido].index.values)

        listaFrecuencia = []

        for val in listaMunicipio:
            listaFrecuencia.append([val,
                                    tabla[miApellido][val]/poblacion[val]])

        df = pd.DataFrame(listaFrecuencia)

        df.columns = ["NAME", "frecuencia"]

        myPalette = px.colors.sequential.Blues

        fig = px.choropleth_mapbox(df,
                                   geojson=mapaMunicipios,
                                   color=df.frecuencia,
                                   range_color=(min(df.frecuencia),
                                                max(df.frecuencia)),
                                   color_continuous_scale=myPalette,
                                   opacity=0.90,
                                   locations="NAME",
                                   featureidkey="properties.NAME",
                                   center={"lat": 18.25178, "lon": -66.264513},
                                   mapbox_style="stamen-terrain",
                                   zoom=8)

        fig.update_layout(margin={"r": 10, "t": 1, "l": 10, "b": 10})

        return fig
    else:
        temp = mapaCoropletico_vacio(mapaMunicipios, miApellido)

    return temp


def mapaCoropletico_vacio(mapaMunicipios, miApellido):

    listaMunicipio = list(tabla.transpose().columns)
    listaFrecuencia = []

    for val in listaMunicipio:
        listaFrecuencia.append([val, 0])

    df = pd.DataFrame(listaFrecuencia)

    df.columns = ["NAME", "frecuencia"]

    myPalette = px.colors.sequential.Reds

    fig = px.choropleth_mapbox(df,
                               geojson=mapaMunicipios,
                               color=df.frecuencia,
                               color_continuous_scale=myPalette,
                               opacity=0.90,
                               locations="NAME",
                               featureidkey="properties.NAME",
                               center={"lat": 18.25178, "lon": -66.264513},
                               mapbox_style="stamen-terrain",
                               zoom=7.5)

    fig.update_layout(margin={"r": 10, "t": 1, "l": 10, "b": 10})

    return fig


def frecuencia(miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        # conteo de apellidos por municipio

        conteo = {}

        for muni in list(poblacion.keys()):
            conteo[muni] = tabla[miApellido][muni]

        # porciento de apellidos por municipio (normalizados por la población)

        porciento = {}

        for muni in list(poblacion.keys()):
            porciento[muni] = round(100*conteo[muni]/poblacion[muni], 2)

        top5 = sorted(porciento.items(), key=lambda x: x[1], reverse=True)[0:5]

        temp5 = [top5[i][0] for i in range(len(top5))]

        masFrecuente = "Es más frecuente en: "

        for val in temp5:

            masFrecuente += val + " "

        return masFrecuente

    else:

        return "Apellido no disponible"


def rank(miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        s = tabla.sum()

        rank = list(
            tabla[s.sort_values(ascending=False).index[0:len(tabla.columns)]].
            columns)

        temp1 = str(rank.index(miApellido) + 1)
        temp2 = str(len(tabla.columns))

        rankPos = "Ocupa la posición número {0} entre {1} \
            apellidos distintos".format(temp1, temp2)

        return rankPos
    else:

        return "Apellido no disponible"


def cantidad(miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        temp1 = tabla.sum()[miApellido]
        temp2 = tabla.sum().sum()

        t1 = f"{temp1:,}"
        t2 = f"{temp2:,}"

        cantidad = "Hay {0} personas con ese apellido \
            de un total de {1}".format(t1, t2)

        return cantidad
    else:

        return "Apellido no disponible"


def similares(miApellido):

    miApellido = miApellido.upper()

    if miApellido in list(tabla.columns):

        miApellido3 = miApellido[0:3]

        df = pd.DataFrame(tabla.columns)

        dfFiltrado = df[df["apellido"].str.slice(0, 3) == miApellido3][0:5]

        dfFiltrado = dfFiltrado[dfFiltrado["apellido"] != miApellido]

        similar = "Apellidos similares: "

        for val in dfFiltrado["apellido"]:
            similar += " " + str(val)

        return similar

    else:

        return " "


if __name__ == "__main__":
    app.run_server(debug=True)
