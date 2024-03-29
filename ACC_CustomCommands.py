### Import dependencies

import json
from typing import List

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np




### Classes
from pandas import DataFrame


class PullData:
    def __init__(self, dir_file: str, sheetname: str, sheetnum: int = 0):
        """
        :param dir: Directory to access the API tokens
        :param sheetname: Name of Google Sheet to access.
        :param sheetnum: The page number to access.
        """
        self.sheetName = sheetname
        self.sheetNum = sheetnum
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        self.CREDS = ServiceAccountCredentials.from_json_keyfile_name(dir_file, self.SCOPES)

    def authClient(self) -> None:
        """

        :return: None. Prints success/failure to console.
        
        Connects to Google Spreadsheets and accesses the named spreadsheet.
        """
        try:
            client = gspread.authorize(self.CREDS)
            self.sheet = client.open(self.sheetName)
            print(f'Successfully authorised {self.sheetName}')
        except:
            print('Error occured in authorisation')
            return

    def getDataFrame(self) -> pd.DataFrame:
        """

        :return: Copy of records DataFrame
        """
        records: pd.DataFrame = pd.DataFrame.from_dict(self.sheet.get_worksheet(self.sheetNum).get_all_records())
        return records.copy()


class Standings:
    def __init__(self, dataframe: pd.DataFrame):
        self.leaderboard: pd.DataFrame = dataframe.copy()
        self.leaderboard = self.leaderboard[['Drivers', 'Total']]
        self.leaderboard.sort_values('Total', axis=0, inplace=True, ascending=False, ignore_index=True)
        self.output: str  = 'CurrentStandings.png'

    def getTable(self) -> None:
        """

        :return: Returns None on image creation
        
        Method creates League Standings table. Saves to main directory as CurrentStandings.png
        """
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
        the_figure.scale(1.5, 2)
        the_figure.auto_set_font_size(False)
        the_figure.set_fontsize(12)
        the_figure.auto_set_column_width(col=list(range(len(self.leaderboard.columns))))

        plt.gcf().canvas.draw()
        points = the_figure.get_window_extent(plt.gcf()._cachedRenderer).get_points()
        points[0,:] -= 4; points[1,:] += 4
        nbbox = Bbox.from_extents(points / plt.gcf().dpi)

        plt.savefig(self.output,
                    bbox_inches=nbbox,
                    pad_inches=3,
                    dpi=100)
        plt.clf()
        return None

class RaceResults:
    def __init__(self, dataframe: pd.DataFrame):
        """

        :param dataframe: Input DataFrame containing the record of race results.
        :type dataframe: pd.DataFrame
        """
        self.output: str = 'RaceResults.png'

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

    def getTable(self) -> None:
        """

        :return: Returns None on image creation
        
        Method creates table of race results. Saves to main directory as RaceResults.png
        """
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
        the_figure.auto_set_font_size(False)
        the_figure.set_fontsize(12)
        the_figure.auto_set_column_width(col=list(range(len(self.results.columns))))

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
        return None


class BestTimes:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        
        :param dataframe: Input DataFrame
        :type dataframe: pd.DataFrame
        """
        self.times: pd.DataFrame = dataframe.dropna(axis=1)
        self.output: str = 'BestTimes.png'
        tracks = self.times.columns.values
        tracks = tracks[~self.times.columns.str.contains('Track')]

        new_cols = []
        for i in np.arange(0, len(tracks), 2):
            new_cols.append(f'{tracks[i]}: {self.times.iat[0, i + 1]}')
            new_cols.append(f'{tracks[i]}: {self.times.iat[0, i + 2]}')

        self.times = self.times[1:]
        self.times.set_index('Track', inplace=True)

        self.times.columns = new_cols

        self.rightpart = self.times.to_numpy()

    def getColours(self):
        """

        :return: colourmap, column colours and row colours
        """
        colours = ['deeppink', 'gainsboro']
        colormap = np.zeros_like(self.rightpart)
        colormap[colormap == 0] = colours[-1]

        colcolours = np.zeros_like(self.times.columns.values)
        colcolours[colcolours == 0] = 'bisque'

        rowcolours = np.zeros_like(self.times.index.values)
        rowcolours[rowcolours == 0] = 'bisque'

        return colormap, colcolours, rowcolours

    def getTable(self) -> None:
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
        return None

class UpdateFigures:
    """
    The UpdateFigures class concatenates the classes into one admin command.
    This reduces the number of requests to the Google Spreadsheet, thus allowing for faster returns.
    Since updates mainly occur after races, no need to poll the spreadsheet many times.

    Introducing a poll for the times command may be beneficial.
    This might implemented in the future
    """

    def __init__(self, dir_file, spreadsheet: str, section: str = 'all'):
        options = ['all', 'standings', 'results', 'times']
        self.updated_images: List[str] = []

        if self.section not in options:
            raise Exception('Argument not in list')

        self.section = section
        self.googledata = PullData(dir_file, spreadsheet)
        self.googledata.authClient()

        if self.section == "standings" or "all":
            standings_command = Standings(self.googledata.getDataFrame())
            standings_command.getTable()
            self.updated_images.append(standings_command.output)
            plt.clf()

        if self.section == "results" or "all":
            results_command = RaceResults(self.googledata.getDataFrame())
            results_command.getTable()
            self.updated_images.append(results_command.output)
            plt.clf()

        if self.section == "times" or "all":
            self.googledata.sheetNum = 1
            times_command = BestTimes(self.googledata.getDataFrame())
            times_command.getTable()
            self.updated_images.append(times_command.output)
            plt.clf()



