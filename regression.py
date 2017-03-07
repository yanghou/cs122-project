# CS 122 Project
#
# Chris Summers

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import getdata
import formatdata
import matplotlib.pyplot as plt


def lin_regression(X, Y, x_var):
    '''
    '''
    model = LinearRegression().fit(X,Y)
    m = model.coef_[0]
    b = model.intercept_
    print(m, b)
    x_max = X.max().iat[0]
    x_min = X.min().iat[0]
    plt.scatter(X,Y, color='blue')
    plt.plot([0,1],[b,m+b], 'r')
    plt.xlim( (x_min, x_max) )
    plt.ylim(0,1)
    plt.xlabel(x_var.title())
    plt.ylabel('Percent voting Trump')
    plt.show()


def run_regressions(df, variables):
    '''
    '''
    for var in variables:
        print(var)
        lin_regression(df[[var]], df.pct_trump, var)
        print('------------------')


def dyadic_partition(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var):
    '''
    '''
    plt.scatter(X_trump, Y_trump, color='red')
    plt.scatter(X_clinton, Y_clinton, color='blue')
    plt.xlabel(x_var.title())
    plt.ylabel(y_var.title())
    plt.show()


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
    df.to_csv("data.csv")
    print("okay")
    #run_regressions(df, variables)
    #run_partitions(df, ['percent white male', 'Gini Coefficient'])
