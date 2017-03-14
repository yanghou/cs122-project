# CS 122 Project
#
# Chris Summers


import formatdata
import numpy as np
import pandas as pd


SUMMARY_FILE_VARS = {'male': '002', 'female': '026', 'female_alt': '017',
                     'whitelatino': 'A', 'black': 'B', 'native': 'C', 
                     'asian': 'D', 'islander': 'E', 'other': 'F',
                     'multiracial': 'G', 'white': 'H', 'latino': 'I'}
VARIABLES = [('B19083_001E', 'gini_coefficient'),
             ('')]


def get_summary_variable_id(char_dict):
    '''
    Takes in a characteristic dictionary with information about a demographic 
    group whose ID is desired, and returns the Census ACS id code for that 
    group.
    '''
    race = char_dict.get('race', None)
    sex = char_dict.get('sex', None)
    if race != None and sex == 'female':
        sex = 'female_alt'

    race_id = SUMMARY_FILE_VARS.get(race, "")
    sex_id = SUMMARY_FILE_VARS.get(sex, "001")

    variable_id = "B01001{}_{}E".format(race_id, sex_id)

    return variable_id


def create_variable_dict(sex=None, race=None, employment=None, income=None, 
    name=None):
    '''
    Creates a dictionary for a potential ACS variable
    '''
    if name == None:
        name = 'p_'
        characteristics = [employment, income, race, sex]
        for c in characteristics:
            if c == None:
                pass
            else:
                name = name + "_" + c
        name = name

    char_dict = {'name': name, 'sex': sex, 'race': race, 'employment': employment, 
        'income': income}
    var_id = get_summary_variable_id(char_dict)
    var_dict = {'id': var_id, 'name': name}
    return var_dict


def get_variables(filename='variables.csv'):
    '''
    Gets the variable info from the csv file.
    '''
    variables = pd.read_csv('variables.csv')
    var_dicts= []
    for var in variables.itertuples():
        var_id = var[1]
        divisor = str(var[2])
        if divisor == 'nan':
            divisor = None
        name = var[3]
        display = var[4]
        d = {'id': var_id, 'divisor': divisor, 'name': name, 'display': display}
        var_dicts.append(d)
    return var_dicts


def get_data():
    '''
    Creates the full data DataFrame, and also returns a list of the variables.
    '''
    var_dicts = get_variables()
    df = formatdata.create_multi_variable_table(var_dicts)
    i = -1 * len(var_dicts)
    variables = df.columns[i:]

    return df, variables


if __name__ == '__main__':
    #var_dicts = get_variables()
    df, variables = get_data()
    print(df)
    
