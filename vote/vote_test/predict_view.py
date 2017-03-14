from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import sys
import csv
import os
import backend

RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')




VAR = ('independent','control')
VARIABLE = [('','')] + [(c,c) for c in VAR]

def legal(string):
    '''
     This function check if the input string represent a legal number.
    '''
    for c in string:
        if type(c)!=type('a') and c!='.':
            return False
    return True

class Predictor(forms.MultiValueField):
    '''
    the predictor class creates a format for each predictor object.
    '''
    def __init__(self,*arg,**kwargs):
        fields = (forms.ChoiceField(label="", choices=VARIABLE, required=False),
                  forms.CharField(),)
        super(Predictor,self).__init__(fields=fields,*arg,**kwargs)
    
    def compress(self,values):
        if len(values)==2:
            if values[0] == 'independent' and values[1] != "":
                raise forms.ValidationError('No value should be specified for independent predictor.')
            if not values[0] and values [1] != "":
                raise forms.ValidationError('You need to select "control" first.')
            if values[1]!="" and not legal(values[1]):
                raise forms.ValidationError('The second input should be a decimal number.')
            if values[1]!="" and float(values[1]) < 0:
                raise forms.ValidationError('The assign value should be positive.')
        return values

class SearchForm(forms.Form):
    # for each predictor, create a object 
    p_female = Predictor(
                          label='Sex(percent of female 0-1):',
                          help_text = 'e.g. CONTROL and 0.6 ( meaning assign the value 0.6 to the percent of female )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_white  = Predictor(
                          label='Race(percent of white 0-1):',
                          help_text = 'e.g. CONTROL and 0.8 ( meaning assign the value 0.8 to the percent of white )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    median_age = Predictor(
                          label='Age(median):',
                          help_text = 'e.g. CONTROL and 35 ( meaning assign the value 35 to the median age )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_no_highschool  = Predictor(
                          label='Education(rate):',
                          help_text = 'e.g. CONTROL and 0.3 ( meaning assign the value 0.3 to rate of hightest eduction level below highschool )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_unemployed  = Predictor(
                          label='Unemployment Rate:',
                          help_text = 'e.g. CONTROL and 0.04 ( meaning assign the value 0.04 to the unemployment rate )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_labor_force  = Predictor(
                          label='Label Force Participation Rate:',
                          help_text = 'e.g. CONTROL and 0.6 ( meaning assign the value 0.6 to rate of labor participation )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    median_income  = Predictor(
                          label='Median Income:',
                          help_text = 'e.g. CONTROL and 70000 ( meaning assign the value 70000 to the median income )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    gini  = Predictor(
                          label='Income Inequality(0-1):',
                          help_text = 'e.g. CONTROL and 0.4 ( meaning assign the value 0.4 to the gini index )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_poverty  = Predictor(
                          label='Poverty(rate):',
                          help_text = 'e.g. CONTROL and 0.74 ( meaning assign the value 0.74 to the poverty index )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    median_mfr_income  = Predictor(
                          label='Manufacturing Earnings(median):',
                          help_text = 'e.g. CONTROL and 50000 ( meaning assign the value 50000 to the mean income in manufacturing industry )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_american  = Predictor(
                          label='Identify as American(percent 0-1):',
                          help_text = 'e.g. CONTROL and 0.8 ( meaning assign the value 0.8 to the percent of Identifying as American )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    p_foreign_born  = Predictor(
                          label='Born in the foreign country(percent 0-1):',
                          help_text = 'e.g. CONTROL and 0.3 ( meaning assign the value 0.3 to the percent of people borned in foreign countries  )',
                          required = False,
                          widget = forms.widgets.MultiWidget(
                                   widgets = (forms.widgets.Select(choices=VARIABLE),
                                              forms.widgets.TextInput
                                             )))
    
    
    
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)


def index(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            # Convert form data to an args dictionary which has two keys 
            # specifying what independent predictors the user cares about
            # and the control variable the user choose and the value the
            # user assign. 
            args = {'independent':[],'control':[]}
            VAR_l = ['p_female','p_white','median_age','p_no_highschool','p_unemployed','p_labor_force',
                     'median_income','gini','p_poverty','median_mfr_income','p_foreign_born','p_american']
            for v in VAR_l:
                pred = form.cleaned_data[v]
                if pred:
                    if pred[0]=='independent':
                        args['independent'].append(v)
                    elif pred[0]=='control':
                        if pred[1]=='':
                            args['control'].append((v,None))
                        else:
                            args['control'].append((v,float(pred[1])))
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)
            try:
                res = backend.analyze(args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_courses:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    else:
        context['result'] = res
        context['num_results']=len(res)
    context['form'] = form
    return render(request, 'predict.html', context)
