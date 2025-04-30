# native modules
import os
import sys
import math

# third party modules
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager  # for fonts
import seaborn as sns


def get_plot_styles():
    """Define color palette, linestyles, and markers for plotting."""
    palette = sns.color_palette("tab10")
    linestyles = ["-", "--", ":"]
    markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h"]
    return palette, linestyles, markers


def plot_ideal_strong_scaling(
    ax, aim_data, x_axis, y_axis, plot_speedup, ideal_scale_from="first"
):
    """Plot ideal strong scaling reference line starting from 'first' or 'last' data point."""
    x = aim_data[x_axis]

    if plot_speedup:
        y = aim_data["speedup"]
    else:
        y = aim_data[y_axis]

    if ideal_scale_from == "first":
        ref_x, ref_y = x.iloc[0], y.iloc[0]
    elif ideal_scale_from == "last":
        ref_x, ref_y = x.iloc[-1], y.iloc[-1]
    else:
        raise ValueError("ideal_scale_from must be 'first' or 'last'")

    if plot_speedup:  # line showing 10x gain on 10x resources increase
        ideal_line = x * (ref_y / ref_x)
    else:  # line showing 10x reduction on 10x resources increase
        ideal_line = ref_x * (ref_y / x)

    ax.plot(
        x.to_numpy(), ideal_line.to_numpy(), linestyle="-.", linewidth=0.5, color="k"
    )


def plot_grouped_data(
    ax,
    aim_data,
    x_axis,
    y_axis,
    y_legend_label,
    name,
    aim,
    color,
    linestyle,
    marker,
    plot_speedup,
    ideal_strong_scaling=False,
    ideal_scale_from="first",
):
    """Plot a single grouped dataset."""
    aim_data = aim_data.sort_values(by=[x_axis], ascending=True)
    T1, N1 = aim_data[y_axis].iloc[0], aim_data[x_axis].iloc[0]
    #     T_1, N_1 = aim_data[y_axis].iloc[-1], aim_data[x_axis].iloc[-1]
    aim_data = aim_data.copy()
    aim_data["speedup"] = T1 / aim_data[y_axis]

    #     aim_data.reset_index(inplace=True)
    if plot_speedup:
        sns.scatterplot(
            data=aim_data,
            x=x_axis,
            y=aim_data["speedup"].to_numpy(),
            s=150,
            color=color,
            marker=marker,
            ax=ax,
        )
        ax.plot(
            aim_data[x_axis].to_numpy(),
            aim_data["speedup"].to_numpy(),
            linestyle,
            color=color,
            marker=marker,
            #                 label=f"{name} - {aim} ({y_legend_label if y_legend_label else y_axis})")
            label=f"{name} - {aim}",
        )
    else:
        sns.scatterplot(
            data=aim_data,
            x=x_axis,
            y=aim_data[y_axis].to_numpy(),
            s=150,
            color=color,
            marker=marker,
            ax=ax,
        )
        ax.plot(
            aim_data[x_axis].to_numpy(),
            aim_data[y_axis].to_numpy(),
            linestyle,
            color=color,
            marker=marker,
            #                 label=f"{name} - {aim} ({y_legend_label if y_legend_label else y_axis})")
            label=f"{name} - {aim}",
        )

    if ideal_strong_scaling:
        plot_ideal_strong_scaling(
            ax, aim_data, x_axis, y_axis, plot_speedup, ideal_scale_from
        )


def extract_and_plot_grouped_data(
    df,
    ax,
    x_axis,
    y_axes,
    col_groupby_color,
    col_groupby_linestyle,
    plot_speedup,
    ideal_strong_scaling,
    ideal_scale_from,
    y_legend_labels=None,
):
    """Extract grouped data and call plotting function within the loop."""
    palette, linestyles, markers = get_plot_styles()

    for y_idx, y_axis in enumerate(y_axes):
        y_legend_label = y_legend_labels[y_idx] if y_legend_labels else None
        linestyle = linestyles[y_idx % len(linestyles)]

        grpby = df.groupby(col_groupby_color)[col_groupby_color].unique()

        for i, name in enumerate(grpby):
            color = palette[i % len(palette)]
            df_plot = df[df[col_groupby_color] == name[0]].sort_values(
                by=col_groupby_linestyle
            )

            for j, aim in enumerate(df_plot[col_groupby_linestyle].unique()):
                marker = markers[j % len(markers)]
                aim_data = df_plot[df_plot[col_groupby_linestyle] == aim].sort_values(
                    by=[x_axis], ascending=True
                )

                plot_grouped_data(
                    ax,
                    aim_data,
                    x_axis,
                    y_axis,
                    y_legend_label,
                    name[0],
                    aim,
                    color,
                    linestyle,
                    marker,
                    plot_speedup,
                    ideal_strong_scaling,
                    ideal_scale_from,
                )


def finalize_plot(ax, xlabel=None, ylabel=None, x_axis="x", y_axes=["y"]):
    """Add labels, legend, and formatting to the plot."""
    ax.set_xlabel(xlabel if xlabel else x_axis, fontsize=25)
    ax.set_ylabel(ylabel if ylabel else ", ".join(y_axes), fontsize=25)
    plt.grid()


def generate_speedup_plot(
    df,
    x_axis,
    y_axes,
    col_groupby_color,
    col_groupby_linestyle,
    xlabel=None,
    ylabel=None,
    plot_speedup=True,
    ax=None,
    ideal_strong_scaling=False,
    ideal_scale_from="first",
    y_legend_labels=None,
):
    """
    Generate a grouped line/scatter plot with optional speedup and ideal scaling lines.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing performance metrics.

    x_axis : str
        Column name to use for the x-axis (e.g., number of processors).

    y_axes : list of str
        List of column names to use as y-axes for plotting.

    col_groupby_color : str
        Column used to group and assign different colors to the lines.

    col_groupby_linestyle : str
        Column used to further group and assign different linestyles/markers.

    xlabel : str, optional
        Custom label for the x-axis. Defaults to `x_axis` if None.

    ylabel : str, optional
        Custom label for the y-axis. Defaults to the y column name(s) if None.

    plot_speedup : bool, default=True
        If True, compute and plot speedup instead of raw y-values.

    ax : matplotlib.axes.Axes
        Existing matplotlib Axes instance where the plot will be drawn.

    ideal_strong_scaling : bool, default=False
        If True, plot an ideal strong scaling reference line.

    ideal_scale_from : {'first', 'last'}, default='first'
        Whether to anchor the ideal scaling line from the
        first or last data point in the x-axis.

    y_legend_labels : list of str, optional
        Custom labels to use in the plot legend, corresponding to `y_axes`.

    Returns
    -------
    None
        The function modifies the provided `ax` in place.
    """
    if ax is None:
        raise ValueError("An existing matplotlib Axes instance must be provided.")

    extract_and_plot_grouped_data(
        df,
        ax,
        x_axis,
        y_axes,
        col_groupby_color,
        col_groupby_linestyle,
        plot_speedup,
        ideal_strong_scaling,
        ideal_scale_from,
        y_legend_labels,
    )
    finalize_plot(ax, xlabel, ylabel, x_axis, y_axes)
