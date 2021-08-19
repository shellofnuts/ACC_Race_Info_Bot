### Import dependencies

import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np

### Classes

class Standings:
    def __init__(self, filename):
        self.leaderboard = pd.read_csv(filename+'.csv', sep=',')
        self.leaderboard = self.leaderboard[['Drivers', 'Total']]
        self.leaderboard.sort_values('Total', axis=0, inplace=True, ascending=False, ignore_index=True)
        self.output = 'CurrentStandings.png'

    def getTable(self):
        colours = ['gold', 'lightsteelblue', 'peru']
        for i in range(len(self.leaderboard.index.values) - 3):
            colours.append('gainsboro')

        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.box(on=None)

        the_figure = plt.table(cellText=np.transpose([self.leaderboard.Drivers.values, self.leaderboard.Total.values]),
                               cellColours=np.transpose([colours, colours]), cellLoc='center',
                               rowLabels=[x + 1 for x in self.leaderboard.index.values],
                               colLabels=['Drivers', 'Total'],
                               loc='center',
                               colWidths=[0.2, 0.2])
        the_figure.scale(1, 1.5)

        plt.gcf().canvas.draw()
        points = the_figure.get_window_extent(plt.gcf()._cachedRenderer).get_points()
        points[0,:] -= 4; points[1,:] += 4
        nbbox = Bbox.from_extents(points / plt.gcf().dpi)

        plt.savefig(self.output,
                    bbox_inches=nbbox,
                    pad_inches=3,
                    dpi=100)

class RaceResults:
    def __init__(self, filename):
        self.filename = filename
        self.output = 'CurrentResults.png'

        self.results = pd.read_csv(filename+'.csv', sep=',')
        self.results.replace("", np.nan, inplace=True)
        self.results.dropna(how='all', axis=1, inplace=True)
        self.results.drop(['Points', 'Result', 'Total'], axis=1, inplace=True)
        rightpart = self.results.drop('Drivers', axis=1).to_numpy()
        self.results.set_index('Drivers', inplace=True)

        # Need to create colour map
        colours = ['gold', 'lightsteelblue', 'peru', 'lightcoral', 'lightskyblue', 'gainsboro']
        self.colormap = np.zeros_like(rightpart)
        places = ['25', '18', '15', 'DNF', 'DNS']
        for i in range(len(places)):
            self.colormap[rightpart == places[i]] =  colours[i]
        self.colormap[self.colormap == 0] = colours[-1]

    def getTable(self):
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.box(on=None)

        the_figure = plt.table(cellText=self.results.to_numpy(),
                               cellColours=self.colormap, cellLoc='center',
                               rowLabels=self.results.index.values,
                               colLabels=self.results.columns.values,
                               loc='center')
        the_figure.scale(1, 1.5)

        plt.gcf().canvas.draw()
        points = the_figure.get_window_extent(plt.gcf()._cachedRenderer).get_points()
        points[0, :] -= 4;
        points[1, :] += 4
        nbbox = Bbox.from_extents(points / plt.gcf().dpi)

        plt.savefig(self.output,
                    bbox_inches=nbbox,
                    pad_inches=3,
                    dpi=100)

class BestTime:
    def __init__(self, user, track):
        self.user = user
        self.track = track
