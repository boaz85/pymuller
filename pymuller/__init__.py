from pymuller.logic import _muller_plot


def muller(populations_df, adjacency_df, ax=None):

    _muller_plot(populations_df, adjacency_df, ax)