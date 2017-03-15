# CS 122 Project
#
# Chris Summers

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
import matplotlib.pyplot as plt


def lin_regression(X, Y):
    '''
    Performs a basic linear regression.
    '''
    linreg = LinearRegression().fit(X, Y)
    b = linreg.coef_
    irct = linreg.intercept_
    r2 = linreg.score(X,Y)
    return b, r2, irct


def run_separate_regressions(predictor_data, dependent_data, predictor_names, plot=False):
    '''
    Run multiple regressions based on the predictor variables given, returns a
    list of tuples with the results of the regressions.
    '''
    rv = []
    for var in predictor_names:
        X = predictor_data[[var]]
        Y = dependent_data
        b, r2, irct = lin_regression(X, Y)
        rv.append((X, Y, b, irct, var))
        if plot:
            plot_single_variable(X, Y, b, irct, var)

    return rv


def run_combined_regressions(predictor_data, dependent_data, predictor_names, 
    pdtr_means, plot=False):
    '''
    Runs a full regression based on all of the predictors given. Returns the 
    results of the regression.
    '''
    ircts_ctrl = []
    X = predictor_data
    Y = dependent_data
    b, r2, irct = lin_regression(X, Y)
    for index, var in enumerate(predictor_names):
        X = predictor_data[[var]]
        other_means = pdt_means[:index] + pdt_means[index+1:]
        other_b = np.concatenate(( b[:,:index], b[:,index+1:] ), axis=1)
        irct_new = irct + np.dot(other_b.T, other_means)
        ircts_ctrl.append(irct_new)
        if plot:
            plot_single_variable(X, Y, b[0][index], irct_new[0][0], var)

    return b, r2, (irct, ircts_ctrl)


class Model(object):

    def __init__(self, data, d_var, i_var, c_var=[], c_values=None, d_data=None, i_data=None, c_data=None):
        self.data = data
        self.d_var = d_var
        
        if type(i_var) != list:
            self.i_var = [i_var]
            print("Independent variable not passed as list")
        elif len(i_var) == 2:
            self.i_var = i_var
        elif len(i_var) > 2:
            self.i_var = i_var[:2]
        elif len(i_var) == 1:
            self.i_var = i_var.append('p_white')
        else:
            self.i_var = ['p_female','p_white']

        if type(c_var) != list:
            self.c_var = [c_var]
            print("Control variable not passed as list")
        else:
            self.c_var = c_var

        if (i_data is None) or (d_data is None):
            self.i_data = data[i_var]
            self.d_data = data[d_var]
        else:
            self.i_data = i_data
            self.d_data = d_data

        if c_data is None:
            self.c_data = data[c_var]
        else:
            self.c_data = c_data

        self.c_values = c_values

        # Set self.expected and self.ranges
        self._get_expected()


    def _get_expected(self):
        '''
        Sets the expected values of the variables of interest and produces
        their value ranges.
        '''
        expected = []
        ranges = []
        for var in self.i_var + self.c_var:
            vcolumn = self.data[[var]]
            vmean = vcolumn.mean()[0]
            vmin = vcolumn.min()[0]
            vmax = vcolumn.max()[0]
            expected.append(vmean)
            ranges.append( (vmin, vmax) )

        self.expected = expected
        self.i_expected = expected[:len(self.i_var)]
        self.c_expected = expected[len(self.i_var):]
        self.ranges = ranges


    def linreg_independent(self, separate=False, plot=False):
        '''
        Runs regressions on the independent variables. Can be run as separate
        regressions or as one single regression.
        '''
        if separate:
            coefs = run_separate_regressions(self.i_data, self.d_data, 
                        self.i_var, plot)
        else:
            coefs = run_combined_regressions(self.i_data, self.d_data, 
                        self.i_var, self.i_expected, plot)

        return coefs


    def control_variables(self, values=None):
        '''
        Controls for Model's control variables
        '''
        X, Y = self.c_data, self.d_data
        b, r2, irct = lin_regression(X, Y)

        ctrl_effect = np.dot(X, b.T)
        controlled = (Y - ctrl_effect)

        if values is None:
            new_ctrl_effect = np.dot(b, self.c_expected)
        else:
            new_expected = []
            for i, n in enumerate(values):
                if n is None:
                    new_expected.append(self.c_expected[i])
                else:
                    new_expected.append(n)
            new_ctrl_effect = np.dot(b, new_expected)

        controlled = controlled + new_ctrl_effect
        return controlled, b, r2, irct


    def get_scaled_coefs(self):
        '''
        Gets normalized linear coefficients for the variables of interest.
        '''
        X = self.data[self.c_var+self.i_var]
        X_scaled = preprocessing.scale(X)
        self.scaled_predictors = X_scaled
        Y = self.d_data

        b, r2, irct = lin_regression(X_scaled, Y)

        b_dict = {}
        for i, var in enumerate(self.c_var + self.i_var):
            b_dict[var] = b[0][i]

        self.scaled_coefs = b_dict

        return b_dict, (b, r2, irct)


    def determine_winner(self, margin, plot=False):
        '''
        Given a county vote DataFrame with new vote margin values, calculate
        which candidate won in each county and return DataFrames of the 
        values for the two variables, as well as the names of those variables.
        '''
        
        trump = self.i_data[margin.margin > 0.0]
        clinton = self.i_data[margin.margin < 0.0]

        X_trump, Y_trump = trump.iloc[:,0], trump.iloc[:,1]
        X_clinton, Y_clinton = clinton.iloc[:,0], clinton.iloc[:,1]
        x_var, y_var = self.i_var[0], self.i_var[1]

        if plot:
            plot_two_variables(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var)

        return X_trump, Y_trump, X_clinton, Y_clinton, x_var, y_var


    def go(self, values=None, plot=False):
        '''
        Runs the analysis of the model, generating the betas and creating the plots
        '''
        controlled, b_ctrl, r2_ctrl, irct_ctrl = self.control_variables(values=values)

        # Get Basic Linear Regression for each i_var
        idv_plot_params = run_separate_regressions(self.i_data, controlled, self.i_var)

        # Get combined graph (uncontrolled)
        comb_plot_params = self.determine_winner(self.d_data)

        # GEt combined graph (controlled)
        comb_plot_params_ctrl = self.determine_winner(controlled)

        # Get scaled coefs
        b_dict, scaled_params = self.get_scaled_coefs()

        # Get variable display names
        variable_display_names = pd.read_csv('variables.csv')
        name_dict = {}
        for i, row in variable_display_names.iterrows():
            name_dict[row['Name in Database']] = row['Axes Name']
        #(row['Name in Interface'], 


        # Plot Graphs
        plt.clf()
        f, axarr = plt.subplots(2,2)
        
        for i, (X, Y, b, irct, x_var) in enumerate(idv_plot_params):
            x_var = name_dict.get(x_var, x_var)
            plot_single_variable(X, Y, b, irct, x_var, ax=axarr[0,i])

        X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var = comb_plot_params
        x_var = name_dict.get(x_var, x_var)
        y_var = name_dict.get(y_var, y_var)
        plot_two_variables(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var, ax=axarr[1,0])
        title = x_var + " vs. " + y_var + " (Uncontrolled)"
        axarr[1,0].set_title(title)

        X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var = comb_plot_params_ctrl
        x_var = name_dict.get(x_var, x_var)
        y_var = name_dict.get(y_var, y_var)
        plot_two_variables(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var, ax=axarr[1,1])
        title = x_var + " vs. " + y_var + " (Controlled)"
        axarr[1,1].set_title(title)


        f.subplots_adjust(hspace=0.35, wspace=0.35)
        f.set_size_inches(10,10, forward=False)
        plt.savefig('analyze.png')

        return b_dict


    def best_k(self, k):
        variables = self.c_var + self.i_var
        v_dict, current_vars, max_r2 = find_best_k(self.data, variables, k)
        return v_dict


def find_best(df, variables, current_vars, best_r2=0.0, verbose=False):
    '''
    Finds the variable with the highest R2.
    '''
    best_var = None
    for var in variables:
        if verbose:
            #print(var)
            pass
        b, r2, irct = lin_regression(df[current_vars+[var]], df.margin)
        if r2 > best_r2:
            best_r2 = r2
            best_var = var

    #print(best_var, ":", r2)
    return best_var, r2


def find_best_k(df, variables, k, threshold=0, verbose=False):
    '''
    Goes through the list of variables, repeatedly choosing the variable that,
    when added, generates the best R2, until k variables have been chosen.
    '''
    remaining_vars = list(variables)
    current_vars = []
    v_dict = {}
    test_vars = []
    current_r2 = 0.0
    best_var = None
    max_r2 = 0.0

    for count in range(k):
        best_var, best_r2 = find_best(df, remaining_vars, current_vars,
            max_r2, verbose)
            
        if best_r2 < max_r2 + threshold:
            return v_dict, current_vars, max_r2
        else:
            v_dict[best_var] = best_r2 - max_r2
            max_r2 = best_r2

        current_vars.append(best_var)
        remaining_vars.remove(best_var)

    return v_dict, current_vars, max_r2


def plot_single_variable(X, Y, b, irct, x_var, ax=None):
    '''
    Creates a plot of a variable vs. the vote margin. Plots the linear
    approximation of the data as well.
    '''
    x_max = X.max().iat[0]
    x_min = X.min().iat[0]
    gap = (x_max - x_min) / 20
    x_max = x_max + gap
    x_min = x_min - gap

    Y_ = Y.where(Y < 1.0, 1.0)
    Y_ = Y_.where(Y > -1.0, -1.0)
    if ax is None:
        plt.scatter(X,Y_, color='blue', alpha=0.1)
        plt.plot([0,1],[irct,b+irct], 'r')
        plt.xlim( (x_min, x_max) )
        plt.ylim(-1,1)
        plt.xlabel(x_var)
        plt.ylabel('Vote Margin (%)')
        plt.show()
    else:
        ax.scatter(X,Y_, color='blue', alpha=0.1)
        ax.plot([0,1],[irct,b+irct], 'r')
        ax.set_title(x_var)
        ax.set_xlim( (x_min, x_max) )
        ax.set_ylim(-1,1)
        ax.set_xlabel(x_var)
        ax.set_ylabel('Vote Margin (%)')
        return ax


def plot_two_variables(X_trump,Y_trump, X_clinton, Y_clinton, x_var, y_var, ax=None):
    '''
    Plots two sets of counties on a two variable plane, where the first set is
    all the counties that voted for Trump, and the second is all the counties 
    that voted for Clinton
    '''
    if ax is None:
        plt.scatter(X_trump, Y_trump, color='red', alpha=0.1)
        plt.scatter(X_clinton, Y_clinton, color='blue', alpha=0.1)
        plt.xlabel(x_var)
        plt.ylabel(y_var)
        plt.show()
    else:
        ax.scatter(X_trump, Y_trump, color='red', alpha=0.1)
        ax.scatter(X_clinton, Y_clinton, color='blue', alpha=0.1)
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        return ax


if __name__ == "__main__":
    
    data = pd.read_csv('data_without_nans.csv',
        dtype={'fips': str, 'state': str, 'county': str})
    data = data.iloc[:,1:]

    d_var = ['margin']
    i_var = ['p_labor_force', 'p_white']
    c_var = ['median_income', 'p_unemployed', 'p_no_highschool']
    m = Model(data, d_var, i_var, c_var)
    
    b_dict = m.go(plot=True)
    v_dict = m.best_k(4)
