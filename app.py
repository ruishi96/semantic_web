import pathlib
import pandas as pd

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import dash_cytoscape as cyto

from utilities.ont import get_cytoscape_elements
from utilities.ont import get_sparql_query_results

# configuration details
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()
df_ontologies = pd.read_csv(DATA_PATH.joinpath("ontologies.csv"))
ontology_list = df_ontologies["Ontology"].unique()
queries_list = pd.DataFrame()
df_query_results = df_ontologies.copy()
ontology_view_elements = []

# format colors: primary, secondary, success, info, warning, danger, light, dark, link
# p-2 mb-2 text-left
title_format = "bg-secondary text-white text-left"
form_heading_format = "bg-primary text-white text-left"
field_label_format = "bg-secondary text-white text-left"
input_format = "text-danger"

# instantiate the Dash server
#
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.VAPOR, dbc_css])
app.config.suppress_callback_exceptions = True

####################################################################################################################
# top container
#
top_container = html.H1("Semantic Web Dashboard",
                        className="bg-primary text-white p-2 mb-2 text-left")

####################################################################################################################
# bottom container
#
bottom_container = html.H6("Brandeis University International Business School",
                           className="bg-primary text-white p-2 mb-2 text-left")

####################################################################################################################
# sidebar container
#
sidebar_container = html.Div(
    [
        html.H4(
            "Ontology", className="bg-primary text-white p-2 mb-2 text-center"
        ),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dcc.Markdown("Select Ontology", className="bg-primary text-white p-2 mb-2 text-center"),
                        dcc.Dropdown(
                            id="ontology-select",
                            placeholder="Select",
                            options=[{"label": i, "value": i} for i in ontology_list],
                        ),
                        html.Br(),
                        html.P("Select Query", className="bg-primary text-white p-2 mb-2 text-center"),
                        dcc.Dropdown(
                            id="query-select",
                            disabled=True,
                            options=[{"label": i, "value": i} for i in ontology_list],
                        ),
                        html.Br(),
                        html.P("Endpoint", className="bg-primary text-white p-2 mb-2 text-center"),
                        dcc.Dropdown(
                            id="endpoint-select",
                            disabled=True,
                            options=[{"label": i, "value": i} for i in ontology_list],
                        ),
                        html.Br(),
                        html.Div(
                            id="submit-button-div",
                            children=[
                                dbc.Button(
                                    id="submit-button",
                                    children="Submit",
                                    n_clicks=0,
                                    disabled=True,
                                    style={'width': '100%'},
                                    className="bg-primary text-white p-2 mb-2 text-center"),
                            ],
                        ),
                    ],
                    title="Ontology",
                ),
                dbc.AccordionItem(
                    [
                        ThemeChangerAIO(aio_id="theme"),
                    ],
                    title="Theme",
                ),
            ],
            start_collapsed=False, always_open=True, flush=True,
        ),
    ],
)

####################################################################################################################
# body container
# view tab
#
body_container_view = \
    html.Div(
        [
            html.H4(
                "Ontology Visualization", className="bg-primary text-white p-2 mb-2 text-center"
            ),
            dcc.Dropdown(
                id='ontology-view-update-layout',
                value='grid',
                clearable=False,
                options=[
                    {'label': name.capitalize(), 'value': name}
                    for name in ['random', 'grid', 'circle', 'concentric', 'breadthfirst', 'cose' ]
                ]
            ),
            cyto.Cytoscape(
                id='ontology-view',
                elements=ontology_view_elements,
                style={'width': '100%', 'height': '1600px'},
            )
        ],
    )


@app.callback(
    Output('ontology-view', 'layout'),
    Input('ontology-view-update-layout', 'value'))
def update_layout(layout):
    return {'name': layout}


####################################################################################################################
# body container
# query tab
#
body_container_query = \
    html.Div(
        [
            html.H4(
                "Query the Ontology", className="bg-primary text-white p-2 mb-2 text-center"
            ),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("Enter a SPARQL Query", className="bg-primary text-white p-2 mb-2 text-left"),
                            dcc.Textarea(
                                id='sparql-query-text',
                                value='',
                                cols='4',
                                disabled=True,
                                style={'width': '100%'},
                            ),
                        ],
                        title="SPARQL",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P("Query Results", className="bg-primary text-white p-2 mb-2 text-left"),
                            dash_table.DataTable(
                                id='query-results-table',
                                data=df_query_results.to_dict('records'),
                                columns=[{'id': c, 'name': c} for c in df_ontologies.columns],

                                page_current=0,
                                page_size=25,
                                fixed_rows={'headers': True},

                                style_cell={'textAlign': 'left'},
                                style_as_list_view=True,

                                row_deletable=False,
                                editable=False,
                                filter_action="native",
                                sort_action="native",
                                style_table={"overflowX": "auto", 'overflowY': 'auto'},
                                export_format="csv",
                            )
                        ],
                        title="RESULTS",
                    ),
                ],
                start_collapsed=False, always_open=True, flush=True,
            ),
        ],
    )

####################################################################################################################
# body container
#
tab_0 = dbc.Tab(body_container_view, label="VIEW")
tab_1 = dbc.Tab(body_container_query, label="QUERY")
body_container = dbc.Card(
    dbc.Tabs([tab_0, tab_1])
)

####################################################################################################################
# layout
#
app.layout = dbc.Container(
    [
        top_container,
        dbc.Row(
            [
                dbc.Col(
                    [
                        sidebar_container,
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        body_container,
                    ],
                    width=10,
                ),
            ]
        ),
        bottom_container,
    ],
    fluid=True,
    className='dbc',
)


####################################################################################################################
# callbacks
#
@app.callback(
    Output("query-select", "options"),
    Output("query-select", "disabled"),
    [Input("ontology-select", "value")]
)
def ontology_select_dropdown_selected(ontology_selected):
    if ontology_selected is None:
        return [{"label": i, "value": i} for i in ontology_list], True

    df = df_ontologies.query(f'Ontology == "{ontology_selected}"')
    query_file_location = df['Sparql'].unique()[0]
    query_df = pd.read_csv(DATA_PATH.joinpath(query_file_location))
    query_name_list = query_df['Name'].unique()
    options = []
    for q in query_name_list:
        options.append({'label': q, 'value': q})
    return options, False


@app.callback(
    Output("endpoint-select", "options"),
    Output("endpoint-select", "disabled"),
    Output("sparql-query-text", "value"),
    Output("sparql-query-text", "disabled"),
    Output("submit-button", "disabled"),
    [Input("query-select", "value")],
    [State("ontology-select", "value")]
)
def query_select_dropdown_selected(query_selected, ontology_selected):
    if ontology_selected is None or query_selected is None:
        return [{"label": i, "value": i} for i in ontology_list], True, '', True, True

    df = df_ontologies.query(f'Ontology == "{ontology_selected}"')
    query_file_location = df['Sparql'].unique()[0]
    query_df = pd.read_csv(DATA_PATH.joinpath(query_file_location))
    query_df.query(f'Name == "{query_selected}"', inplace=True)
    endpoint_list = query_df['Endpoint'].unique()
    endpoint_options = []
    for e in endpoint_list:
        endpoint_options.append({'label': e, 'value': e})
    sparql_query = query_df['Sparql'].unique()[0]
    return endpoint_options, False, sparql_query, False, False


@app.callback(
    Output("query-results-table", "data"),
    Output("query-results-table", "columns"),
    Output("ontology-view", "elements"),
    [Input("submit-button", "n_clicks")],
    [State("endpoint-select", "value"),
     State("sparql-query-text", "value")]
)
def submit_button_selected(n_clicks, endpoint_selected, sparql_query_text):
    if n_clicks == 0 or endpoint_selected is None or sparql_query_text is None:
        data = df_ontologies.to_dict('records')
        columns = [{'id': c, 'name': c} for c in df_ontologies.columns]
        return data, columns, ontology_view_elements

    results_table, results_columns = get_sparql_query_results(endpoint_selected, sparql_query_text)
    cytoscape_elements = get_cytoscape_elements(endpoint_selected)

    return results_table, results_columns, cytoscape_elements


##############################################
# Run the server
#
if __name__ == "__main__":
    app.run_server(debug=True)
