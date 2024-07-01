import numpy as np
import plotly.graph_objects as go


def graph_by_key(
    datadict: str,
    key_list: list[str],
    x_key: str,
    title: str,
    export_path: bool = None,
    show_fig=True,
    fig=None,
    yaxis_title="",
    log_x=False,
    return_html=False
):
    if fig == None:
        fig = go.Figure()

    for y_key in key_list:
        fig.add_trace(
            go.Scatter(
                x=datadict[x_key],
                y=datadict[y_key],
                name=y_key,
                mode="lines",
            )
        )

    if log_x:
        fig.update_layout(
            title=title, xaxis_title=x_key, xaxis_type="log", yaxis_title=yaxis_title
        )
    else:
        fig.update_layout(title=title, xaxis_title=x_key, yaxis_title=yaxis_title)

    if show_fig:
        fig.show()

    if export_path:
        fig.write_html(export_path)

    if return_html:
        return fig.to_html(full_html=False)


def graph_datadict(
    datadict: str,
    x_key: str,
    title: str = "",
    export_path: str = None,
    show_fig=True,
    fig=None,
    yaxis_title="",
    log_x=False,
    return_html = False
):
    key_list = [key for key in datadict if key != x_key]

    html = graph_by_key(
        datadict=datadict,
        key_list=key_list,
        x_key=x_key,
        title=title,
        export_path=export_path,
        show_fig=show_fig,
        fig=fig,
        yaxis_title=yaxis_title,
        log_x=log_x,
        return_html=return_html
    )

    if return_html:
        return html


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
