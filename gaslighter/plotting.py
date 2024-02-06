import numpy as np
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
    export_path: str = None,
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

# def graph_countour(
#     datadict,
#     x_key,
#     y_key,
#     z_title,
#     z_data,
#     title: str = "" ,
#     export_path: bool = None,
#     show_fig = True,
#     fig = None
# ):


#     if fig is None:
#         fig = go.Figure()

#     fig.data=[go.Surface(z=z_data, x=_x, y=_y)]

#     fig.update_layout(
#         scene=dict(
#             title=title,
#             xaxis_title=x_key,
#             yaxis_title=y_key,
#             zaxis_title=z_title
#         )
#     )

#     if show_fig:
#         fig.show()

#     if export_path:
#         fig.write_html(export_path)