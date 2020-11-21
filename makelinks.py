from pathlib import Path

files = """ep2017ae_02_del_ninno_cloud_trasferimento_internazionale.pdf
ep2017ae_02_del_ninno_cloud_trasferimento_internazionale.ppt
ep2017ae_03_la_muscatella_diritti_dati_perduti.pdf
ep2017ae_03_la_muscatella_diritti_dati_perduti.ppt
ep2017ae_04_agostini_cloud_se_lo_conosci_lo_apprezzi.pdf
ep2017ae_05_pedrazzi_cloud_aldila_nuvole.pdf
ep2017ae_06_costantini_destefani_alvise_problema_prova_digitale.pdf
ep2017ae_07_gobbato_reaponsabilita_privacy_nella_nuvola.pdf
ep2017ae_08_ferri_privacy_questione_carattere.pdf
ep2017ae_09_longo_privacy_e_pa.pdf
ep2017ae_09_longo_privacy_e_pa_2.pdf
ep2017ae_10_scire_tutela_identita_digitale.pdf
ep2017ae_12_giorio_cloud_o_non_cloud.pptx
ep2017ae_12_giorio_cloud_o_non_cloud_relazione.pdf
ep2017ae_13_blengino_senor_procure_nelle_nuvole.pdf
ep2017ae_13_blengino_senor_procure_nelle_nuvole_handout.pdf
ep2017ae_14_zugnaz_privacy_anima.pdf
ep2017ae_21_senor_processo_capi-incolpazione.pdf""".split()

imgs = {
    '.pdf': 'presentation',
    '.ppt': 'presentation-ppt',
    '.pptx': 'presentation-ppt',
    '.pdh': 'handouts',
    '.pdo': 'document',
    '.url': 'link',
    '.unk': 'unknown',
}

STR = "[![{}](/images/icon/{}.png)](http://urna.winstonsmith.org/materiali/2017we/atti/{})"

for fname in files:
    fpath = Path(fname)
    suffix = fpath.suffix
    if suffix not in imgs:
        suffix = '.unk'
    logo = imgs[suffix]
    if suffix[:3] == '.pd':
        suffix = '.pdf'
    print(STR.format(suffix[1:],logo,fname))
    
