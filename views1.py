from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import sys
import csv
import os
from operator import and_
from pres16 import graph_test
from functools import reduce

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
        county='county',
        fips='fips',
        candidate='cand',
        strict='st',
        pct_report = 'pct_report',
        votes ='votes',
        tvotes='total_votes',
        pct = 'pct',
        lead = 'lead'
)


ABBRE = ("US","AK","AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","GU","HI","IA","ID", "IL","IN","KS","KY","LA","MA","MD","ME","MH","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY", "OH","OK","OR","PA","PR","PW","RI","SC","SD","TN","TX","UT","VA","VI","VT","WA","WI","WV","WY")
CAND = ('Donald Trump','Hillary Clinton')
S_C=('STATE','COUNTY')
CANDIDATES = [('','')]+[(c,c) for c in CAND]
STATES =[('','')]+ [(state_abb,state_abb) for state_abb in ABBRE]
STATE_COUNTY = [('','')]+[(sc,sc)for sc in S_C]

class cand_stats(forms.MultiValueField):
    def __init__(self,*arg,**kwargs):
        fields = (forms.ChoiceField(label='Candidate Name',choices=CANDIDATES,required=False),
                  forms.ChoiceField(label='State or County',choices = STATE_COUNTY,required=False),)
        super(cand_stats,self).__init__(fields=fields,*arg,**kwargs)
    
    def compress(self,values):
        if len(values) == 2:
            if values[0] is None or not values[1]:
                raise forms.ValidationError("Must specify both candidate name and State or County level")
        return values

class SearchForm(forms.Form):
    state = forms.ChoiceField(
            label='State Name Abbrieviation',
            choices=STATES,
            required=False)
    county = forms.CharField(
             label = "County Name",
             help_text='e.g. Bexar County',
             required =False,
             )
    cand_stat = cand_stats(
             label = 'Winner Details',
             help_text = 'e.g. Donald Trump and STATE',
             required = False,
             widget = forms.widgets.MultiWidget(
                widgets=(forms.widgets.Select(choices=CANDIDATES),
                         forms.widgets.Select(choices=STATE_COUNTY)
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
            # Convert form data to an args dictionary for graph_test
            args = {}
            state = form.cleaned_data['state']
            if state:
                args['state'] = state
            county = form.cleaned_data['county']
            if county:
                args['county'] = county
            cand_stat = form.cleaned_data['cand_stat']
            print(cand_stat)
            if cand_stat:
                args['cand_name']=cand_stat[0]
                args['S_C']=cand_stat[1]
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)
            try:
                res = graph_test(args)
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
    elif res == 'graph':
        context['result'] = True
    else:
        context['cand_name']=args['cand_name']
        context['S_C']=args['S_C']
        context['result'] = res
        context['num_results']=len(res)
    context['form'] = form
    return render(request, 'index.html', context)
