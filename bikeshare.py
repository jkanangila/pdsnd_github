import pandas as pd
from time import sleep as seconds

class Bikeshare(object):
    
    @staticmethod
    def input_request(msg1, msg2, valid_choices):
        """
        Request input from user and check if it has been entered corectly.

        args
            (strt): msg1 - display to request input from user
            (strt): msg2 - dispays if the input is enterred incorrectly
            (list): valid_choices - a list of allowed characters used to check integrity of inputs
        Return
            (str) response of the input
        """
        r = input(msg1)
        while True:
            try:
                # '_'.join is for cases were the user type "new york city" (with spaces). Lower and strip is to enable program to handle 
                # most types of inputs
                r = '_'.join(r.split()).lower().strip()
                if r in valid_choices:
                    return r
            except:
                pass

            r = input(msg2)
    
    def __init__(self):
        
        # request wether the results should be displayed for a specific town only and get user reply
        self.filter_by_town = self.input_request(("Would you like to filter the results by town? If yes enter the town's name or symbol. Else, type 'n'."
                                 + "\nValid towns are: chicago (c), new york city (ny), washington (w). | "), 
                               "Invalid characters found in your answer! Please make sure you spelled your answer corectly: ",
                              ('chicago', 'c', 'new_york_city','ny', 'washington', 'w', 'n'))

        # request wether the results should be displayed for a specific month only and get user reply
        self.filter_by_month = self.input_request(("\nWould you like to see the results for a specific month only? \nIf yes enter the month's name"
                                         + " or a number where 1 is for january. Else, type 'n'."
                                         + "\nValid months are: january, february, march, april, may, june. | "), 
                                       "Invalid characters found in your answer! Please make sure you spelled your answer corectly:",
                                      ('april', 'february', 'january', 'june', 'march', 'may', 'n', '1','2','3','4','5','6'))

        self.filter_by_day_of_week = self.input_request(("\nWould you like to see the results for a specific day of the week only? \nIf yes enter"
                                                    + " the day's name or a number where 0 is for monday. Else, type 'n'. | \n"), 
                                       "Invalid characters found in your answer! Please make sure you spelled your answer corectly: ",
                                      ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 
                                       'saturday', 'sunday', 'n', '0','1','2','3','4','5', '6'))

    def load_data(self):
        """
        Return a pandas dataframe in which data are filtered using the user's inputs.
        """
        # Filter data by town
        # If the user does not wish to filter the results by town, load and merge all the datapoints, for all the cities
        if self.filter_by_town == 'n':
            df1 = pd.read_csv('chicago.csv', parse_dates=['Start Time', 'End Time'])
            df2 = pd.read_csv('new_york_city.csv', parse_dates=['Start Time', 'End Time'])
            df3 = pd.read_csv('washington.csv', parse_dates=['Start Time', 'End Time'])
            df = pd.concat([df1, df2, df3], sort=True, join='inner')
        # Otherwise, load data for the city specified by the user
        else:
            # The try clause handles instances were the user typed-in the full name of the city
            try:
                df = pd.read_csv(self.filter_by_town + '.csv', parse_dates=['Start Time', 'End Time'])
            # The except clause handles cases were the user typed-in a symbol of the city
            except:
                keys = dict(zip(['c', 'ny', 'w'], ['chicago','new_york_city','washington']))
                df = pd.read_csv(keys[self.filter_by_town] + '.csv', parse_dates=['Start Time', 'End Time'])
        
        # If the loaded dataframe contains a column called birth year, rename it to age group
        try:
            df.rename(columns={'Birth Year':'Age Group'}, inplace=True)
        except:
            pass
        
        # Slice the data to display data for the specified month only
        if self.filter_by_month != 'n':
            # For instances were a month number is given
            try:
                df = df[df['Start Time'].dt.month == int(self.filter_by_month)]
            # For instances were a month name is given
            except:
                df = df[df['Start Time'].dt.month_name() == self.filter_by_month.capitalize()]
                
        # Slice the data to display data for the specified day of the week only
        if self.filter_by_day_of_week != 'n':
            try:
                # For instances were a day number is given
                df = df[df['Start Time'].dt.dayofweek == int(self.filter_by_day_of_week)]
            except:
                # For instances were a day name is given
                df = df[df['Start Time'].dt.day_name() == self.filter_by_day_of_week.capitalize()]
                
        return df
    
    def basic_stas(self):
        """Returns some basic statics (highest count, lowest count, mean, ....) for each columns of the dataframe"""
        df = self.load_data()
        output = {}
        
        def stats_param(df, _dict, item):
            # Identigy maximum and minimum counts, and respective frequencies for the provided dataframe.
            # store the results in the provided dictionary using item as key
            counts = df.groupby(item).count()['Unnamed: 0']
            _dict[item]['most_popular'] = counts.idxmax()
            _dict[item]['freq_most_popular'] = int(counts.max())
            _dict[item]['least_popular'] = counts.idxmin()
            _dict[item]['freq_least_popular'] = int(counts.min())
            _dict[item]['value_count'] = len(counts)
        
        for item in df.columns:
            # create output dictionary
            output[item] = {}
            
            # Obtain a statistical describe of columns containing object type data using stats_param() defined above.
            # The same method will also be used to describe columns containing birth years.
            if df[item].dtypes == "O" or item == 'Age Group':
                stats_param(df, _dict=output, item=item)
                
            # Since trip duration contains numeric data, a different set of statistical parameters are used to describe its contents. 
            elif item == 'Trip Duration':
                counts = df[item].describe()
                output[item]['max'] = int(counts.max())
                output[item]['mean'] = int(counts.mean())
                output[item]['min'] = int(counts.min())
                
            # For columns containing datetime type data, return the statistics in terms of months, days, and hours
            elif item in ['Start Time', 'End Time']:
                df1 = df.copy()
                # Add new columns containing the month, day, andd hour. 
                df1['month'], df1['day'] = df1[item].dt.month_name(), df1[item].dt.day_name()
                df1['hour'] = df1[item].dt.hour
                for i in ['month', 'day', 'hour']:
                    output[item][i] = {}
                    # Don't compute the statistics if there is only one type of data in the column.
                    if len(df1[i].unique()) != 1:
                        stats_param(df=df1, _dict=output[item], item=i)
                        
        return output
    
    def reports(self):
        """Print descriptive statistics for each columns in the filtered dataframe"""
        print("\n\nGathering and processing data, standby...\n")
        s = self.basic_stas()
        sleep = 8
        for i in ['Start Station', 'End Station', 'Trip Duration', 'Age Group', 'Gender', 'User Type', 'Start Time', 'End Time']:
            if i == 'Unnamed: 0':
                continue
            elif i in ('Age Group', 'Gender') and self.filter_by_town in ('washington', 'w', 'n'):
                continue
                
            try:
                print("There were {p[value_count]} {}s. ".format(i.lower(), p=s[i])
                + "\nThe most popular {} was '{p[most_popular]}' with a frequency of {p[freq_most_popular]}".format(i.lower(), p=s[i])
                + "\nThe least popular {} was '{p[least_popular]}' with a frequency of {p[freq_least_popular]}\n".format(i.lower(), p=s[i]))
                print("\nProcesssing data, standby...\n")
                seconds(sleep)
            except:
                try:
                    print("The maximum {} was {p[max]}, the average was {p[mean]}, and the minimum was {p[min]}\n".format(
                        i.lower(), i.lower(), i.lower(), p=s[i]))
                    print("\nProcesssing data, standby...\n")
                    seconds(sleep)
                except:
                    for j in s[i].keys():
                        try:
                            if self.filter_by_month != 'n' and j == 'month' or self.filter_by_day_of_week != 'n' and j == 'day':
                                continue
                                
                            print("The most popular {}ing {} was '{p[most_popular]}'. {p[freq_most_popular]} trips {}ed at that time".format(i.split()[0].lower(), j.lower(), i.split()[0].lower(), p=s[i][j])
                            + "\nThe least popular {}ing {} was '{p[least_popular]}'. {p[freq_least_popular]} trips {}ed at that time\n".format(i.split()[0].lower(), j.lower(), i.split()[0].lower(), p=s[i][j]))
                            print("\nProcesssing data, standby...\n")
                            seconds(sleep)
                        except:
                            pass
                        
        
        # Display raw data for the user
        request = self.input_request('Would you like to see raw data? Y/N: ', 
                                "Invalid characters found in your answer! Please make sure you spelled your answer corectly: ", 
                                ('y', 'n'))
        print("\nProcesssing request. standby...\n")
        raw_data = self.load_data()
        start, stop = 0, 5
        # while loop to 5 rows of raw data until either: the user enters "n" or the there are no more raw data to display
        while request == 'y':
            print(raw_data[start:stop])
            print("")

            request = self.input_request('Would you like to see more data? Y/N: ', 
                                    "Invalid characters found in your answer! Please make sure you spelled your answer corectly: ", 
                                    ('y', 'n'))
            start += 5
            stop += 5
            if stop > len(raw_data):
                print("No more raw data to display.")
                break

Bikeshare().reports()