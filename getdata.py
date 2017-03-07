# CS 122 Project
#
# Chris Summers


import formatdata


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
    '''
    if name == None:
        name = ''
        characteristics = [employment, income, race, sex]
        for c in characteristics:
            if c == None:
                pass
            else:
                name = name + c + "_"
        name = name[:-1]

    char_dict = {'name': name, 'sex': sex, 'race': race, 'employment': employment, 
        'income': income}
    var_id = get_summary_variable_id(char_dict)
    var_dict = {'id': var_id, 'name': name}
    return var_dict


def get_variables():
    '''
    '''
    women = create_variable_dict('female')
    white = create_variable_dict(race='white')
    black = create_variable_dict(race='black')
    latino = create_variable_dict(race='latino')
    white_men = create_variable_dict('male', 'white')
    gini = {'id': 'B19083_001E', 'name': 'gini', 'type': 'value'}

    var_dicts = [women, white, black, latino, white_men, gini]

    df = formatdata.create_multi_variable_table(var_dicts)

    return df


if __name__ == '__main__':
    df = get_variables()
    print(df)