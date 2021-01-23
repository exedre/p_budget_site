# coding: utf-8

"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
import re
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from pathlib import Path
import click

import logging
LOGGER = logging.getLogger("PWS")
logging.basicConfig(level=logging.INFO)

### ---------------------------------------- CONFIGURATION

SPREADSHEET_ID = '1-y_YAyjJ9wqsF1Z1aEbe_H1-naqjEwSH60K-t8HUWXs'

CONTI = 'CONTI'

PATH = 'content/'

## ---------------------------------------- FINE CONFIGURAZIONE

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

#### ---------------------------------------- READ FUNCTIONS

def read_value(service, id, range, tweak_item=None):
    result = service.spreadsheets().values().get(spreadsheetId=id,
                                                 range=range).execute()
    values = result.get('values', [])
    if tweak_item:
        values = tweak_item(values)
    if len(values)==1:
        val = values[0]
        if len(val)==1:
            v = val[0]
            if v[0]=='€':
                return float(re.sub(',','',v[1:]))
            try:
                v = float(v)
            except ValueError:
                pass
            return v
        return val
    else:
        return values

def read_db(service, id, range, tweak_item=None, tweak_collection=None):
    result = service.spreadsheets().values().get(spreadsheetId=id,
                                                 range=range).execute()
    values = result.get('values', [])
    infos = {}
    if not values:
        print('No data found.')
    else:
        return values

def read_db_into_dict(service, id, range, tweak_item=None, tweak_collection=None):
    result = service.spreadsheets().values().get(spreadsheetId=id,
                                                 range=range).execute()
    values = result.get('values', [])
    infos = {}
    if not values:
        print('No data found.')
    else:
        for jj,row in enumerate(values):
            if jj == 0:
                HEADERS = row
                continue
            if len(row[0]):
                info = dict(zip(HEADERS, row))
                info['label'] = info['LNK'].lower()
                if tweak_item:
                    info = tweak_item(info)
                infos[info['label'].lower()] = info
    if tweak_collection:
        infos = tweak_collection(infos)
    return infos

#### ---------------------------------------- END READ FUNCTIONS


#### ---------------------------------------- SETUP SYNC SHEET

def setup_sheet_work(SPREADSHEET_ID):
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--debug-section', type=click.Choice(['db', 'program']))
def main(debug,debug_section):
    LOGGER.info('service beginning')
    service = setup_sheet_work(SPREADSHEET_ID)
    LOGGER.info('service loaded')
    conti = read_db(service, SPREADSHEET_ID, CONTI)
    pprint(conti)
    values = {}
    values = setup_db(conti,values)
    fields = 'OB_ISCR,OB_BIL,DATA,A_DONORBOX,C_FEE,CARTA_TINABA,CHECK,CONTI,CONTO_TINABA,DISPONIBILE,FEE_DONORBOX,FEE_PAYPAL,FEE_STRIPE,FEE_TOTALI,GRANTOTALE,RESIDUAL_DONORBOX,TOT_DONORBOX,A_PAYPAL,A_STRIPE,A_TINABA,TOTALE,TOTALI,CE_COSTI,CE_RICAVI,SP_ATTIVITA,SP_PASSIVITA,DESC_CONTI,DESC_SOTTOCONTI,DESCRIZIONE_BILANCIO'.split(',')
    for field in fields:
        value = read_value(service, SPREADSHEET_ID, field)
        values[field] = value
        print(field,"=",value)
    values['JDATA']=re.sub(r'(\d+)/(\d+)/(\d\d\d\d) (\d+):(\d+):(\d+)',r'\3\2\1',values['DATA'])
    values['FDATA']=re.sub(r'(\d+)/(\d+)/(\d\d\d\d) (\d+):(\d+):(\d+)',r'\3-\2-\1',values['DATA'])
    import datetime
    s = re.sub(r'(\d+)/(\d+)/(\d\d\d\d) (\d+):(\d+):(\d+)',r'\3_\2_\1',values['DATA'])
    theday = datetime.date(*map(int, s.split('_')))
    prevday = theday - datetime.timedelta(days=1)
    values['JDATAY']=prevday.strftime('%Y%m%d')
    if debug and debug_section=='db':
        pprint(values)
        return
    for n,label in enumerate('ISCRIZIONI,DONAZIONI,ALTRO,PAGAMENTI'.split(',')):
        values[label]=values['TOTALI'][n]
    descrizioni = dict([ (k,v) for k,v in values['DESCRIZIONE_BILANCIO']])
    values['DESCRIZIONI']=descrizioni
    values['BILANCIO'] = {}
    values = setup_bilancio(values,'CE_COSTI',descrizioni,
                            lambda x: -x if x < 0 else x)
    values = setup_bilancio(values,'CE_RICAVI',descrizioni)
    values = setup_bilancio(values,'SP_ATTIVITA',descrizioni)
    # debiti = values['A_CRED'] - values['R_CRED']
    # values['P_DEB']=debiti
    values = setup_bilancio(values,'SP_PASSIVITA',descrizioni)
    utile_o_perdita = values['R_T'] - values['C_T']
    if utile_o_perdita > 0:
        # Utile
        values['TBL_CE_RICAVI'].append(["----",'----'])
        values['TBL_CE_COSTI'].append(["Utile d'esercizio",utile_o_perdita])
        values['TBL_CE_COSTI'].append(["Totale a pareggio",values['C_T']+utile_o_perdita])
        values['TBL_CE_RICAVI'].append(["Totale a pareggio",values['R_T']])
        values['TBL_SP_ATTIVITA'].append(["----",'----'])
        values['TBL_SP_PASSIVITA'].append(["Utile d'esercizio",utile_o_perdita])
        values['TBL_SP_ATTIVITA'].append(["Totale a pareggio",values['A_T']])
        values['TBL_SP_PASSIVITA'].append(["Totale a pareggio",values['P_T']+utile_o_perdita])
    else:
        # Perdita
        values['TBL_CE_RICAVI'].append(["Perdita d'esercizio",-utile_o_perdita])
        values['TBL_CE_COSTI'].append(["----",'----'])
        values['TBL_CE_COSTI'].append(["Totale a pareggio",values['C_T']])
        values['TBL_CE_RICAVI'].append(["Totale a pareggio",values['R_T']+utile_o_perdita])
        values['TBL_SP_ATTIVITA'].append(["Perdita d'esercizio",-utile_o_perdita])
        values['TBL_SP_PASSIVITA'].append(["----",'----'])
        values['TBL_SP_PASSIVITA'].append(["Totale a pareggio",values['P_T']])
        values['TBL_SP_ATTIVITA'].append(["Totale a pareggio",values['A_T']+utile_o_perdita])
    # values = setup_iscrizioni(values,db)
    pprint(values)
    values = setup_table(values,'TBL_SP_ATTIVITA','TBL_SP_PASSIVITA','STATO_PATRIMONIALE')
    values = setup_table(values,'TBL_CE_COSTI','TBL_CE_RICAVI','CONTO_ECONOMICO')
    write_out(PATH,'finanze-ppit', **values)
    values = setup_movimenti(values,conti)
    write_out(PATH,'movimenti-ppit', **values)
    values = setup_json(values,conti)
    write_json(PATH,'pp-it', False, **values)
    write_json(PATH,'pp-it', True, **values)


def setup_json(values,conti):
    srow = []
    colnames = []
    colpub = {}
    for num,row in enumerate(conti):
        print("A",row)
        if re.match(r'^DEFN',row[0]):
            colnames.extend(row)
            continue
        if re.match(r'^DEFK',row[0]):
            for col,cell in enumerate(row):
                colnames[col] = row[col]+"."+colnames[col]
            continue
        if re.match(r'^DEFP',row[0]):
            continue
        srow.append(row)
    donazioni = list(filter(lambda x: x[3]=='DONA',srow))[1:]
    iscrizioni = list(filter(lambda x: x[3]=='ISCR',srow))
    ob_iscr = float(values['OB_ISCR'])
    ob_bil  = float(values['OB_BIL'])
    d_num = len(donazioni)
    d_val = sum(map(lambda x: float(x[4]),donazioni))
    d_last = donazioni[-1][6]
    i_num = len(iscrizioni)
    i_val = sum(map(lambda x: float(x[4]),iscrizioni))
    i_last = iscrizioni[-1][6]
    perc_i = i_num / ob_iscr
    perc_b = (d_val + i_val) / ob_bil
    import json
    dict = {
        'date': values['FDATA'],
        'i_n': i_num,
        'i_val': i_val,
        'i_last': i_last,
        'i_avg': i_val / i_num,
        'd_n': d_num,
        'd_val': d_val,
        'd_last': d_last,
        'd_avg': d_val / d_num,
        'perc_i': perc_i,
        'perc_b': perc_b
    }
    values['JSON'] = json.dumps(dict)
    return values
    # Cosa pubblicare nel json
    # - numero totale di iscrizioni
    # - valore medio dell'iscrizione
    # - data ultima iscrizione
    # - progressione iscrizioni
    # - d_num numero totale di donazioni
    # - d_val valore medio della donazione
    # - d_last data ultima donazione
    # - d_prog progressione donazioni
    # - percentuale di raggiungimento dell'obiettivo di iscrizioni
    # - percentuale di raggiungimento dell'obiettivo economico


def setup_movimenti(values,conti):
    srow = []
    colnames = []
    colpub = {}
    for num,row in enumerate(conti):
        print("A",row)
        if re.match(r'^DEFN',row[0]):
            colnames.extend(row)
            continue
        if re.match(r'^DEFK',row[0]):
            for col,cell in enumerate(row):
                colnames[col] = row[col]+"."+colnames[col]
            continue
        if re.match(r'^DEFP',row[0]):
            for col,cell in enumerate(row):
                print(col,cell,colnames[col])
                if not re.match('^[0-9]',cell):
                    colnames[col] = None
                else:
                    colpub[int(float(cell))-1] = col
            continue
        srow.append(row)
    table = []
    tabrow = [ [] for x in colpub]
    for col,k in colpub.items():
        tabrow[col]=values['DESCRIZIONI'][colnames[k]]
    table.append(tabrow)
    tabrow = [ "---" for x in colpub]
    table.append(tabrow)
    for row in srow:
        print(row)
        tabrow = [ [] for x in colpub]
        # import pdb; pdb.set_trace()
        for col,k in colpub.items():
            print(col,k,row[k])
            tabrow[col]=tweak_val(float(row[k])) if table[0][col]=='€' else row[k]
        table.append(tabrow)
    rows = "\n".join([ '|' + '|'.join(row) for row in table])
    values['MOVIMENTI_CONTABILI']=rows
    return values

def setup_table(values,tb1,tb2,lab):
    tbl1 = values[tb1]
    tbl2 = values[tb2]
    tbls = [tbl1,tbl2]
    o12 = 0 if len(tbl1)>=len(tbl2) else 1
    o21 = 1 - o12
    M = max(len(tbl1),len(tbl2))
    k = M-min(len(tbl1),len(tbl2))
    table = []
    for j in range(0,M,+1):
        print("TABLE:",M-1,k,j)
        if len(tbl1)>0:
            t1 = tbl1.pop()
        else:
            t1 = ['','']
        if len(tbl2)>0:
            t1 += tbl2.pop()
        else:
            t1 += ["",""]
        print(t1)
        table.append("|"+"|".join([ tweak_val(x) for x in t1]))
    table.append("|-|-|-|-")
    values[lab]=("|\n".join(reversed(table)))
    return values

def tweak_val(val):
    if isinstance(val,str):
        if re.match(r'^-',val):
            return ""
    if isinstance(val,float):
        return "€ {:2,.2f}".format(val)
    return val

def setup_bilancio(values,sezione,descrizioni,tweak=lambda x: x):
    costi = values[sezione]
    bilancio = {}
    valoriz = []
    for jj,row in enumerate(costi):
        print(jj,row)
        if len(row)==0:
            continue
        label = row[0]
        if len(row)==2:
            if re.match(r' *>',row[1]):
                print("FORMULA=",row[1])
                formula = re.split('\+',re.sub("[\> ]+","",row[1]))
                valore = 0.0
                for component in formula:
                    sign = 1.0
                    if component[0]=='-':
                        component = component[1:]
                        sign = -1.0
                    if component in values:
                        print(component,"=",sign,"*",values[component] )
                        val =  float(re.sub('€','',str(values[component])))
                        valore += val * sign
                valore=tweak(valore)
                values[label]=valore
                descrizione = descrizioni[label] if label in descrizioni else label
                valoriz.append( [descrizione,valore] )
            # here calc
            continue
        label = row[0]
        if len(label)==0:
            continue
        if label[0]=='-':
            valoriz.append(['----','-----'])
            continue
        if label in values:
            valore=tweak(values[label])
            values[label]=valore
            descrizione = descrizioni[label] if label in descrizioni else label
            valoriz.append( [descrizione,valore] )
    values['TBL_'+sezione]=valoriz
    return values

def setup_db(conti,values):
    db = {}
    for jj,row in enumerate(conti):
        if row[0]=='DEFN':
            headers = row
            continue
        elif row[0]=='DEFK':
            sectors = row
            headers = [ s + "_" + h for h,s in zip(headers,sectors)]
            continue
        elif row[0]=='DEFP':
            continue
        dictionary = dict(zip(headers,row))
        label = dictionary['_CONTO'] + "_" + dictionary['_SOTTOC']
        amount = float(dictionary['_AMMONTARE'])
        print(jj,label,"=",amount)
        if label not in db:
            db[label]=0.0
        db[label]+=amount
    return db


if __name__ == '__main__':
    main()
