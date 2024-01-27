import plotly.graph_objects as go

# TODO Add titles
# TODO Implement plottly yaml?
def graph_by_key(
    datadict: str,
    key_list: list[str],
    x_key: str,
    title: str,
    export_path: bool = None,
    show_fig = True,
    fig = None
):
    if fig == None:
        fig = go.Figure()

    for y_key in key_list:
        fig.add_trace(
            go.Scatter(
                x=datadict[x_key],
                y=datadict[y_key],
                name=y_key,
                mode="lines"
            )
        )
    fig.update_layout(
        title = title,
        xaxis_title = x_key
    )
    if show_fig:
        fig.show()

    if export_path:
        fig.write_html(export_path)


def graph_datadict(
    datadict: str,
    x_key: str,
    title: str,
    export_path: bool = None,
    show_fig = True,
    fig = None
):
    key_list = [key for key in datadict]

    graph_by_key(
        datadict=datadict,
        key_list=key_list,
        x_key=x_key,
        title=title,
        export_path=export_path,
        show_fig=show_fig,
        fig=fig
    )
