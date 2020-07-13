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

        return [identity] + sum([get_inner_order(c) for c in children_identities], []) + [identity]

    order = []

    for strain in sorted(adjacency_df['Identity'].unique()):
        if strain not in order:
            order += get_inner_order(strain)

    return np.array(order)


def _muller_plot(populations_df, adjacency_df, smoothing_std=10, normalize=False, ax=None):

    ordering = _get_strains_ordering(adjacency_df)

    if normalize:
        populations_df['Population'] = populations_df.groupby('Generation')['Population'].transform(lambda x:
                                                                                                    x / x.sum())

    population_size_max = populations_df.groupby('Generation')['Population'].sum().max()
    generations = populations_df['Generation'].max() - populations_df['Generation'].min()

    pivot = populations_df.pivot(index='Generation', columns='Identity', values='Population')
    pivot = pivot.rolling(generations, 1, True, 'gaussian').mean(std=smoothing_std).clip(0, population_size_max)

    Y = pivot[ordering] / 2
    Y = Y.to_numpy().T
    x = populations_df['Generation'].unique()

    normed = (ordering - ordering.min()) / (ordering.max() - ordering.min())
    colors = matplotlib.cm.terrain(normed)

    if ax is None:
        fig, ax = plt.subplots()

    ax.stackplot(x, Y, colors=colors)
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency' if normalize else 'Abundance')