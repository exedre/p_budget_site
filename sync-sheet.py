from datetime import datetime,timedelta
import mysql.connector as mysql
import json
from pathlib import Path
import click
import re
import logging
LOGGER = logging.getLogger("PWS")
logging.basicConfig(level=logging.INFO)

PATH = 'content/'

def write_out(path, fname, **kw):
    templ_f = Path(path) / (fname+'.template')
    out_f = Path(path) / ( fname + '-' + kw['JDATA'] + '.md')
    templ = templ_f.read_text(encoding='utf-8')
    output = templ.format(**kw)
    out_f.write_text(output)
    print("scrittura "+str(out_f)+" from template "+str(templ_f))

def write_json(path, fname, fdatap, **kw):
    templ_f = Path(path) / (fname+'.template')
    if fdatap:
        if not (Path(path) / 'json').exists():
            (Path(path) / 'json').mkdir()
        out_f = Path(path) / 'json' / ( fname + '-' + kw['JDATA'] + '.json')
    else:
        out_f = Path(path) / ( fname + '.json')
    templ = templ_f.read_text(encoding='utf-8')
    output = templ.format(**kw)
    out_f.write_text(output)
    print("scrittura "+str(out_f)+" from template "+str(templ_f))


db = mysql.connect(
    host = "localhost",
    user = "it_reri",
    passwd = "Damien8cool",
    database = "it_reri_mailman_mautic",

)

# numero di form relativi alle petizioni
params = {
    'petition_cat': 8,
    'ended_petition_cat': 9,
    'onboarding_min_form': 4,
    'onboarding_med_form': 1,
    'onboarding_max_form': 9,
    'deleted_form': 6,
    }

queries = {
    'all' :   'SELECT COUNT(*) from ma_leads',
    'leads': 'SELECT COUNT(*) from ma_leads where email is not NULL',
    'named': 'SELECT COUNT(*) from ma_leads where email is not NULL and firstname is not NULL',
    'onboard_min': 'SELECT COUNT(S.lead_id) from ma_form_submissions S WHERE S.form_id = {onboarding_min_form}',
    'onboard_med': 'SELECT COUNT(S.lead_id) from ma_form_submissions S WHERE S.form_id = {onboarding_med_form}',
    'onboard_max': 'SELECT COUNT(S.lead_id) from ma_form_submissions S WHERE S.form_id = {onboarding_max_form}',
    'deleted': 'SELECT COUNT(S.id) from ma_form_submissions S WHERE S.form_id = {deleted_form}',
    'all_petitions': 'SELECT COUNT(*) from ma_forms where category_id in ({petition_cat},{ended_petition_cat})',
    'petitions': 'SELECT COUNT(*) from ma_forms where category_id = {petition_cat}',
    # firmatari di tutte le petizioni
    'petsign' : 'SELECT COUNT(S.lead_id) from ma_form_submissions S JOIN ma_forms F on S.form_id = F.id where F.category_id = {petition_cat}',
    # firmatari unici
    'dpetsign' : 'SELECT COUNT(DISTINCT(S.lead_id)) from ma_form_submissions S JOIN ma_forms F on S.form_id = F.id where F.category_id = {petition_cat}',
}

def make_queries(db,results,params,prefix,**queries):
    inresults=results
    for name,query in queries.items():
        cursor = db.cursor()
        executing = query.format(**params)
        print(name, executing)
        cursor.execute(executing)
        records = cursor.fetchall()
        if prefix:
            inresults[prefix+"_"+name]=records
        else:
            inresults[name]=records
    return inresults

results = {}
results = make_queries(db,results,params,None,**queries)

queries = {
    'leads': 'SELECT id,firstname,lastname,email,city,last_active from ma_leads where email is not NULL',
    'petitions': 'SELECT * from ma_forms where category_id = {petition_cat}',
}

data = {}
data = make_queries(db,data,params,None,**queries)

leads = dict([ (x[0],x) for x in data['leads'] ])
# PETITIONS

common = {}
multiple = {}
preport = ["|||||\n|-|-|-|-|"]
for petition in data['petitions']:
    pid = petition[0]
    name =petition[12]
    alias =petition[13]
    print(pid,name)
    params['petition_id']=pid
    queries = {
        'dsigners': 'SELECT COUNT(DISTINCT(lead_id)) from ma_form_submissions where form_id = {petition_id}',
        'fromfb': 'SELECT COUNT(DISTINCT(lead_id)) from ma_form_submissions where form_id = {petition_id} AND referer LIKE "%fbclid%"',
    }
    results = make_queries(db,results,params,prefix="P_{}".format(pid),**queries)
    pprep = []
    for lab in queries.keys():
        pprep.append("|{}|{}|{}|{}|".format(pid,name,lab,results["P_{}_{}".format(pid,lab)]))
    preport.append('\n'.join(pprep))
    dqueries = {
        'subscribers': 'SELECT * from ma_form_submissions WHERE form_id = {petition_id}',
    }
    data[pid] = {}
    data[pid] = make_queries(db,data[pid],params,None,**dqueries)
    for subscriber in map(lambda x: x[3],data[pid]['subscribers']):
        if not subscriber:
            continue
        if subscriber not in common:
            common[subscriber] = []
        if pid not in common[subscriber]:
            common[subscriber].append(pid)
        else:
            if pid not in multiple:
                multiple[pid] = []
            if subscriber not in multiple[pid]:
                multiple[pid].append(subscriber)
results['PETREP']='\n'.join(preport)
morethan1 = dict(filter(lambda x: x[0] and len(x[1])>1,common.items()))
maxis = list(map(lambda x: (len(x[1]),x) ,morethan1.items()))
amaxis = {}
for n,v in maxis:
    if n not in amaxis:
        amaxis[n] = {}
    amaxis[n][v[0]]=v[1]

petitions = dict([ (x[0],x) for x in data['petitions']])
multi_single = {}
MS = "|ID|Pet|Nome|Cognome|email|||\n|-|-|-|-|-|-|-|\n"
for x,y in multiple.items():
    petname = petitions[x][12]
    prow = []
    plead = {}
    for lid in y:
        L=leads[lid]
        plead[lid]=L
        prow.append("|{}|{}|{}|{}|{}|{}|{}|".format(x,petname,L[0],L[1],L[2],L[3],L[4]))
    multi_single[x]=plead
    MS+="\n".join(prow)
results['MULTI_SINGLE']=MS

multi_multi = {}
MM="| "*(7+len(petitions))+"|\n"+"|-"*(7+len(petitions))+"|\n"
for x,y in amaxis.items():
    multi_multi[x] = []
    prow=[]
    for lid,pids in y.items():
        multi_multi[x].append((lid,(leads[lid],pids)))
        L = leads[lid]
        prow.append("|{}|{}|{}|{}|{}|{}|{}|".format(x,lid,L[0],L[1],L[2],L[3],L[4])+'|'.join([ petitions[x][12] for x in pids])+"|")
    MM+="\n".join(prow)
results['MULTI_MULTI']=MM


# MVP

#
# firmatari ad almeno due petizioni
# firmatari a tutte le petizioni


today = datetime.now()

# dd/mm/YY


results['JDATA'] = today.strftime("%Y%m%d")
results['FDATA'] = today.strftime("%Y-%m-%d")
results['DATA'] = today.strftime("%Y-%m-%d %H:%S")

theday = today
prevday = theday - timedelta(days=1)
results['JDATAY'] = prevday.strftime('%Y%m%d')


write_out(PATH,'report', **results)
