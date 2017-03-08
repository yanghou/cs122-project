# CS 122 Project
#
# Chris Summers

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import getdata
import formatdata
import matplotlib.pyplot as plt


def lin_regression(X, Y, verbose=False):
    '''
    '''
    model = LinearRegression().fit(X,Y)
    m = model.coef_
    b = model.intercept_

    r2 = model.score(X,Y)
    if verbose:
        print("m:", m, "b:", b)
        print("R^2:", r2)
    return m, b, r2


def plot_single_variable(X,Y,m,b,x_var):
    '''
    '''
    x_max = X.max().iat[0]
    x_min = X.min().iat[0]
    plt.scatter(X,Y, color='blue')
    plt.plot([0,1],[b,m+b], 'r')
    plt.xlim( (x_min, x_max) )
    plt.ylim(0,1)
    plt.xlabel(x_var.title())
    plt.ylabel('Trump Vote Share')
    plt.show()


def plot_two_variables(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var):
    '''
    '''
    plt.scatter(X_trump, Y_trump, color='red')
    plt.scatter(X_clinton, Y_clinton, color='blue')
    plt.xlabel(x_var.title())
    plt.ylabel(y_var.title())
    plt.show()


def run_regressions(df, variables):
    '''
    '''
    for var in variables:
        print(var)
        lin_regression(df[[var]], df.margin)
        print('------------------')


def find_best(df, variables, current_vars, best_r2=0.0, verbose=False):
    best_var = None
    for var in variables:
        if verbose:
            print(var)
        m, b, r2 = lin_regression(df[current_vars+[var]], df.margin, 
            verbose)
        if r2 > best_r2:
            best_r2 = r2
            best_var = var

    print(best_var, ":", r2)
    return best_var, r2


def find_best_K(df, variables, k, threshold=0, verbose=False):
    remaining_vars = list(variables)
    current_vars = []
    test_vars = []
    current_r2 = 0.0
    best_var = None
    max_r2 = 0.0

    for count in range(k):
        best_var, best_r2 = find_best(df, remaining_vars, current_vars,
            max_r2, verbose)
            
        if best_r2 < max_r2 + threshold:
            return current_vars, max_r2
        else:
            max_r2 = best_r2

        current_vars.append(best_var)
        remaining_vars.remove(best_var)

    return current_vars, max_r2


def run_partitions(df, variables):
    '''
    '''
    for i, var in enumerate(variables[:-1]):
        if i % 2 == 0:
            x_var = var
            y_var = variables[i+1]
            trump = df[df.lead == 'Donald Trump']
            clinton = df[df.lead == 'Hillary Clinton']
            dyadic_partition(trump[[x_var]], trump[[y_var]], 
                clinton[[x_var]], clinton[[y_var]], x_var, y_var)



if __name__ == "__main__":
    df, variables = getdata.get_data()
    print(variables)
    #df.to_csv("data.csv")
    #run_regressions(df, variables)
    #best_vars, max_r2 = find_best_K(df,variables, 8)
    #print(best_vars)
    #print(max_r2)
    #run_partitions(df, ['percent white male', 'Gini Coefficient'])
