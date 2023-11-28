import matplotlib.pyplot as plt
import pandas as pd
from pymuller import muller

populations_df = pd.DataFrame(  # Example with 7 generations and 5 strains
    {'Generation': [i for i in range(7) for _ in range(5)],
     'Identity':   [i for _ in range(7) for i in range(5)],
     'Population': [2, 0, 0, 0, 0,
                    3, 1, 1, 0, 0,
                    6, 3, 2, 1, 0,
                    8, 6, 4, 2, 1,
                    7, 7, 5, 0, 4,
                    5, 10, 3, 0, 6,
                    2, 11, 2, 0, 9]}
)

adjacency_df = pd.DataFrame(
    {'Parent': [0, 0, 1, 2],
     'Identity': [1, 2, 3, 4]}
)

print(adjacency_df)
print(populations_df)

color_series = pd.Series(list(range(5)), index=list(range(5)), name='Color')

muller(populations_df, adjacency_df, color_by=color_series, background_strain=False, colormap='jet', smoothing_std=.5)
plt.show()
