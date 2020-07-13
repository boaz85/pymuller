import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def _get_strains_ordering(adjacency_df):

    children_by_parent = adjacency_df.groupby('Parent')['Identity'].apply(lambda x: list(sorted(list(x))))

    def get_inner_order(identity):

        d = children_by_parent.get(identity, [])

        if len(d) == 0:
            return [identity, identity]

        r = []

        for s in d:
            r += get_inner_order(s)

        return [identity] + r + [identity]

    order = []

    for strain in sorted(adjacency_df['Identity'].unique()):
        if strain not in order:
            order += get_inner_order(strain)

    return np.array(order)


def _muller_plot(populations_df, adjacency_df, smoothing_std=10, ax=None):

    ordering = _get_strains_ordering(adjacency_df)

    x = populations_df['Generation'].unique()

    population_size_max = populations_df.groupby('Generation')['Population'].sum().max()

    pivot = populations_df.pivot(index='Generation', columns='Identity', values='Population')
    pivot = pivot.rolling(300, 20, True, 'gaussian').mean(std=smoothing_std).clip(0, population_size_max)

    Y = pivot[ordering] / 2
    Y = np.array(Y.values.tolist()).T

    normed = (ordering - ordering.min()) / (ordering.max() - ordering.min())
    colors = matplotlib.cm.terrain(normed)

    if ax is None:
        fig, ax = plt.subplots()

    ax.stackplot(x, Y, colors=colors)