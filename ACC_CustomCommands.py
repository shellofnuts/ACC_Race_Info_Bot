### Import dependencies

import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np

### Classes
from pandas import DataFrame


class PullData:
    def __init__(self, sheetname: str, sheetnum: int):
        self.sheetName = sheetname
        self.sheetNum = sheetnum
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        self.CREDS = ServiceAccountCredentials.from_json_keyfile_name('acc-project-sheetskey.json', self.SCOPES)

    def authClient(self):
        try:
            client = gspread.authorize(self.CREDS)
            self.sheet = client.open(self.sheetName)
            print(f'Successfully authorised {self.sheetName}')
        except:
            print('Error occured in authorisation')
            return

    def getDataFrame(self):
        records: DataFrame = pd.DataFrame.from_dict(self.sheet.get_worksheet(self.sheetNum).get_all_records())
        return records


class Standings:
    def __init__(self, dataframe: DataFrame):
        self.leaderboard = dataframe.copy()
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
        plt.clf()

class RaceResults:
    def __init__(self, dataframe: DataFrame):
        self.output = 'CurrentResults.png'

        self.results = dataframe.copy()
        self.results.replace("", np.nan, inplace=True)
        self.results.dropna(how='all', axis=1, inplace=True)
        self.results.drop(['Points', 'Result', 'Total'], axis=1, inplace=True)
        rightpart = self.results.drop('Drivers', axis=1).to_numpy()
        self.results.set_index('Drivers', inplace=True)

        # Need to create colour map
        colours = ['gold', 'lightsteelblue', 'peru', 'lightcoral', 'lightskyblue', 'gainsboro']
        self.colormap = np.zeros_like(rightpart)
        places = [25, 18, 15, 'DNF', 'DNS']
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
        points[0, :] -= 4
        points[1, :] += 4
        nbbox = Bbox.from_extents(points / plt.gcf().dpi)

        plt.savefig(self.output,
                    bbox_inches=nbbox,
                    pad_inches=3,
                    dpi=100)
        plt.clf()

class BestTimes:
    def __init__(self, dataframe: DataFrame):
        self.times = dataframe
        print(self.times.head())
        self.output = 'TimesTable.png'
        tracks = self.times.columns.values
        tracks = tracks[~self.times.columns.str.contains('Track')]



        new_cols = []
        for i in np.arange(0, len(tracks), 2):
            new_cols.append(f'{tracks[i]}: {self.times.iat[0, i + 1]}')
            new_cols.append(f'{tracks[i]}: {self.times.iat[0, i + 2]}')

        #self.times.replace(np.nan, "", inplace=True)

        self.times = self.times[1:]
        self.times.set_index('Track', inplace=True)

        self.times.columns = new_cols

        self.rightpart = self.times.to_numpy()

    def getColours(self):
        colours = ['deeppink', 'gainsboro']
        colormap = np.zeros_like(self.rightpart)
        colormap[colormap == 0] = colours[-1]

        colcolours = np.zeros_like(self.times.columns.values)
        colcolours[colcolours == 0] = 'bisque'

        rowcolours = np.zeros_like(self.times.index.values)
        rowcolours[rowcolours == 0] = 'bisque'

        return colormap, colcolours, rowcolours

    def getTable(self):
        ax = plt.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.box(on=None)

        colormap, colcolours, rowcolours = self.getColours()


        the_figure = plt.table(cellText=self.times.to_numpy(),
                               cellColours=colormap, cellLoc='center',
                               rowLabels=self.times.index.values,
                               colLabels=self.times.columns.values,
                               loc='center',
                               colColours=colcolours,
                               rowColours=rowcolours,
                               fontsize = 26)

        the_figure.scale(1, 1.5)
        the_figure.auto_set_font_size(False)
        the_figure.set_fontsize(12)
        the_figure.auto_set_column_width(col=list(range(len(self.times.columns))))


        plt.gcf().canvas.draw()
        points = the_figure.get_window_extent(plt.gcf()._cachedRenderer).get_points()
        points[0, :] -= 4
        points[1, :] += 4
        nbbox = Bbox.from_extents(points / plt.gcf().dpi)

        plt.savefig(self.output,
                    bbox_inches=nbbox,
                    pad_inches=3,
                    dpi=100)
        plt.clf()