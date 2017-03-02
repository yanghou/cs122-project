# CS 122 Project
#
# Christopher Summers

import numpy as np
import pandas as pd
import urllib3
import json

SUMMARY_FILE_URL = "http://api.census.gov/data/2015/acs5?"
SUBJECT_TABLE_URL = "http://api.census.gov/data/2015/acs5/subject?"
ELECTION_FILE = "./pres16results.csv"

SUMMARY_FILE_VARS = {'male': '002', 'female': '026',
                     'whitelatino': 'A', 'black': 'B', 'native': 'C', 
                     'asian': 'D', 'islander': 'E', 'other': 'F',
                     'multiracial': 'G', 'white': 'H', 'latino': 'I'}


def get_election_results():
    '''
    '''
    election_results = pd.read_csv(ELECTION_FILE, dtype=str)
    columns = list(election_results.columns.values)
    columns = ['county_name'] + columns[1:]
    election_results.columns = columns
    #election_results = election_results[election_results.cand.isin(
    #    ["Hillary Clinton", "Donald Trump"])]
    election_results = election_results[
        election_results.cand == "Hillary Clinton"]

    election_results = election_results[election_results.fips.str.len() != 2]
    election_results = election_results.dropna()
    election_results.fips = election_results.fips.str.pad(5, fillchar="0")
    election_results.sort_values('fips', inplace=True)

    election_results.insert(2, 'state', election_results.fips.str.slice(0,2))
    election_results.insert(3, 'county', election_results.fips.str.slice(2))  

    return election_results


def create_pandas_from_url(url):
    '''
    '''
    pm = urllib3.PoolManager()
    r = pm.request('GET', url)
    table = json.loads(r.data.decode('utf-8'))
    array = np.array(table[1:])
    df = pd.DataFrame(array[1:], columns=table[0])

    return df


def get_summary_file_table(variables, state="*", county="*"):
    '''
    '''
    # Get the total population (B01001_001E) and all other variables chosen
    get_string = "get=NAME,B01001_001E," + ",".join(variables)
    for_string = "&for=county:{}&in=state:{}".format(county, state)
    url = SUMMARY_FILE_URL + get_string + for_string
    df = create_pandas_from_url(url)

    # Convert population numbers to percentages of total
    columns = ['B01001_001E'] + variables
    df[columns] = df[columns].astype(np.float32)
    for column_name, series in df[variables].iteritems():
        df[column_name] = series / df['B01001_001E']

    return df


def get_summary_variable_id(sex=None, race=None):
    '''
    '''
    race_id = SUMMARY_FILE_VARS.get(race, "")
    sex_id = SUMMARY_FILE_VARS.get(sex, "001")
    variable_id = "B01001{}_{}E".format(race_id, sex_id)

    return variable_id


def get_data(test_race=False, test_sex=False, state="*", county="*"):
    '''
    '''
    variable_values = [(None,None)]
    sexes = ['male', 'female']
    races = ['white', 'black', 'latino', 'asian', 'islander']
    if test_sex:
        variable_values = [(x,None) for x in sexes]
    if test_race:
        l = []
        for x,y in variable_values:
            l = l + [(x,z) for z in races]
        variable_values = l

    variables = []
    for sex, race in variable_values:
        variables.append(get_summary_variable_id(sex, race))

    demographics = get_summary_file_table(variables, state=state, county=county)
    election_results = get_election_results()

    df = pd.merge(election_results, demographics, on=['state','county'])
    whatever = ['fips', 'pct'] + list(df.columns)[12:]
    rv = df.loc[:,tuple(whatever)]
    return rv


def regression():
    '''
    '''
    return 0.3141516


def go(test_race=False, test_sex=False):
    '''
    '''
    df = get_data(test_race, test_sex)
    rv = regression(df)
    return rv


if __name__ == '__main__':
    #election_results = get_election_results()
    #print(election_results)

    #variables = [get_summary_variable_id('male','black')]
    #state = "01"
    #df = get_summary_file_table(variables, state=state)
    #print(df)
    data = get_data(test_race=True, test_sex=False, state="05")
    print(data)