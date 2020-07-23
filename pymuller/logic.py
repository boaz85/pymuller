import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def _get_strains_ordering(adjacency_df):

    children_by_parent = adjacency_df.groupby('Parent')['Identity'].apply(lambda x: list(sorted(x)))

    def get_inner_order(identity):

        children_identities = children_by_parent.get(identity, [])

        if len(children_identities) == 0:
            return [identity, identity]

        inner = [get_inner_order(c) for c in children_identities]
        return [identity] + sum(inner, []) + [identity]

    order = []

    identities = list(set(adjacency_df['Identity'].values) | set(adjacency_df['Parent'].values))

    for strain in sorted(identities):
        if strain not in order:
            order += get_inner_order(strain)

    return np.array(order)


def _get_y_values(populations_df, adjacency_df, smoothing_std):

    ordering = _get_strains_ordering(adjacency_df)
    population_size_max = populations_df.groupby('Generation')['Population'].sum().max()
    generations = populations_df['Generation'].max() - populations_df['Generation'].min()

    pivot = populations_df.pivot(index='Generation', columns='Identity', values='Population').sort_index()
    pivot = pivot.rolling(generations, 1, True, 'gaussian').mean(std=smoothing_std).clip(0, population_size_max)

    Y = pivot[ordering] / 2

    # Avoid middle lines. Double leaf clones.
    keep = [0]

    for i, c in enumerate(Y.columns[1:], 1):
        if c == Y.columns[i - 1]:
            Y.iloc[:, i] *= 2
            keep.pop()

        keep.append(i)

    return Y.iloc[:, keep]


def _muller_plot(populations_df, adjacency_df, color_by, colormap='terrain', colorbar=True, background_strain=True,
                 smoothing_std=10, normalize=False, ax=None, click_callback=None):

    if normalize:
        populations_df['Population'] = populations_df.groupby('Generation')['Population'].transform(lambda x:
                                                                                                    x / x.sum())

    x = populations_df['Generation'].unique()
    y_table = _get_y_values(populations_df, adjacency_df, smoothing_std)

    final_order = y_table.columns.values
    Y = y_table.to_numpy().T

    cmap = plt.get_cmap(colormap)
    color_by = color_by.copy()
    ordered_colors = color_by.loc[final_order]
    norm = matplotlib.colors.Normalize(vmin=np.min(ordered_colors), vmax=np.max(ordered_colors))
    colors = cmap(norm(ordered_colors.values))

    if background_strain:
        colors[0] = colors[-1] = [1, 1, 1, 1]

    if ax is None:
        fig, ax = plt.subplots()

    else:
        fig = ax.figure if hasattr(ax, 'figure') else ax.fig

    ax.stackplot(x, Y, colors=colors)

    if colorbar:
        cax = fig.add_axes([0.92, 0.13, 0.02, 0.7])
        cb = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)
        cb.set_label(color_by.name)

    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency' if normalize else 'Abundance')

    plt.sca(ax)

    if click_callback is not None:

        def onclick(event):

            generation = int(np.round(event.xdata))
            row = y_table.loc[generation]
            identity = row[row.cumsum() > event.ydata].index[0]

            click_callback(generation, identity)

        fig.canvas.mpl_connect('button_press_event', onclick)

    return ax