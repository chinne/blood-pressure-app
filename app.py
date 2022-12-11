# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import base64
import io

import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table
from dash import dcc, no_update
from dash.dependencies import Input, Output, State

from utils import (
    create_connection,
    init_db,
    get_critical_values,
    transform_df_date,
)

DB_NAME = "measurement.db"

# Local Postgres
# engine = create_engine("postgresql://postgres:postgres@localhost:5432/measurement")

app = Dash(__name__)

upload_component = dcc.Upload(
    children=['"Drag and Drop" oder ', html.A("Datei auswählen")],
    id="upload",
    className="upload_component",
    style={
        "width": "60%",
        "height": "60px",
        "margin": "auto",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
    },
)

submit_button = html.Button(
    "Daten visualisieren", id="submit-val", n_clicks=0, style=dict(display="none")
)

app.layout = html.Div(
    children=[
        dcc.Store(id="main_data"),
        html.H1(children="Visualisierung der Blutdruckmessung"),
        html.Div(
            children="""Die Webanwendung zeigt kritische Werte der Blutdruckmessung an. Im folgenden kann die Datei (.csv) hochgeladen werden:"""
        ),
        upload_component,
        html.Div(id="output-data-upload"),
        submit_button,
        dcc.Graph(id="time-series-chart", style=dict(display="none")),
    ]
)


def parse_contents(contents, filename):
    decoded = base64.b64decode(contents.split(",")[1]).decode('utf-8')
    try:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded))
        df = transform_df_date(df)
        conn = create_connection(DB_NAME)
        db_cols = list(pd.read_sql("SELECT * FROM pulse_data", con=conn))
        df.rename(columns=dict(zip(df.columns, db_cols)), inplace=True)
        # ‘multi’: Pass multiple values in a single INSERT clause
        df.to_sql("pulse_data", index=False, con=conn, if_exists="append", method='multi')
        data = df.to_dict("records")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing the file."])

    return (
        html.Div(
            [
                html.H5(filename),
                dash_table.DataTable(
                    data,
                    [{"name": i, "id": i} for i in df.columns],
                    fixed_rows={"headers": True},
                    style_table={"height": "300px", "overflowY": "auto"},
                    style_cell={"minWidth": 95, "maxWidth": 95, "width": 95},
                    tooltip_header={
                        "Systolisch (mmHg)": "Der systolische Blutdruck misst den Druck beim Herzschlag – also wenn sich der Herzmuskel zusammenzieht und sauerstoffreiches Blut in die Gefäße pumpt.",
                        "Diastolisch (mmHg)": "Der diastolische Blutdruck misst den Druck auf die Gefäße, wenn der Herzmuskel erschlafft. Der diastolische Druck ist niedriger als der systolische.",
                        "Puls (bpm)": "In der Regel entspricht der Puls der Herzfrequenz, also dem Herzschlag pro Minute.",
                    },
                    tooltip_delay=0,
                    tooltip_duration=None,
                    # Style headers with a dotted underline to indicate a tooltip
                    style_header_conditional=[
                        {
                            "if": {"column_id": col},
                            "textDecoration": "underline",
                            "textDecorationStyle": "dotted",
                        }
                        for col in [
                            "Systolisch (mmHg)",
                            "Diastolisch (mmHg)",
                            "Puls (bpm)",
                        ]
                    ],
                ),
                html.Hr(),  # horizontal line
            ]
        ),
        data,
    )


@app.callback(
    Output("output-data-upload", "children"),
    Output("submit-val", "style"),
    Output("main_data", "data"),
    Input("upload", "contents"),
    State("upload", "filename"),
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children, data = parse_contents(list_of_contents, list_of_names)
        return children, dict(), data
    return no_update


@app.callback(
    Output("time-series-chart", "figure"),
    Output("time-series-chart", "style"),
    State("main_data", "data"),
    Input("submit-val", "n_clicks"),
)
def update_df(data, n_clicks):
    df = pd.DataFrame(data)
    if df.empty is True:
        return 2 * [no_update]
    fig = px.line(df, x="Datum", y=df.columns[1:4])
    critical_list = get_critical_values(df)
    for critical in critical_list:
        fig.add_vline(
            x=critical, line_width=1.5, line_dash="dash", line_color="DarkRed"
        )
    return fig, dict()


if __name__ == "__main__":
    init_db(DB_NAME)
    app.run_server(debug=True)
