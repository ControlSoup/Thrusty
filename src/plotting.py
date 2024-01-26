import plotly.graph_objects as go

# TODO Add titles
# TODO Implement plottly yaml?
def graph_by_key(
    datadict: str,
    key_list: list[str],
    x_key: str,
    export_path: bool = None,
    fig = None
):
    if fig == None:
        fig = go.Figure()

    for y_key in key_list:
        fig.add_trace(
            go.Scatter(
                x=datadict[x_key],
                y=datadict[y_key],
                name=x_key,
                mode="lines"
            )
        )


def graph_datadict(
    datadict: str,
    x_key: str,
    export_path: bool = None,
    fig = None
):
    key_list = [key for key in datadict]

    graph_by_key(datadict, key_list, x_key, export_path, fig)
