import os
import numpy as np
import pandas as pd
import json
import openpyxl
import argparse

#Leer las records de un json
KEYS_TO_USE = ['programId','pppCode','profecha','hourFrom','hourTo','program','matCodesAssigned','avg_rating','boxoffice','classification','genres','runs_available','time_available','boxoffice_percentil']
KEYS_TO_USE_IN_DF = ['programId','pppCode','profecha','hourFrom','hourTo','program','matCodesAssigned', 'matName','avg_rating','boxoffice','classification','genres','runs_available','time_available','boxoffice_percentil']

JSON_PATH = os.path.join('Request-files','output-test.json')

#******* MATS *******#
MATS_PATH = os.path.join('Input-files','mats-27-07.csv')
df_mats = pd.read_csv(MATS_PATH, index_col='matCode') #Definimos el indice matCode
df_unique_mats = df_mats

#Limpio los datos
df_unique_mats = df_unique_mats.drop('genre', 1)
df_unique_mats = df_unique_mats.drop('mmrClasification', 1)
df_unique_mats = df_unique_mats.drop('feedCode', 1)
df_unique_mats = df_unique_mats.drop('anioProd', 1)
df_unique_mats = df_unique_mats.drop('matType', 1)
df_unique_mats.drop_duplicates(subset=None, keep='first', inplace=True)

#******* PROG *******#
PROG_PATH = os.path.join('Input-files','prog-27-07.csv')
df_progs = pd.read_csv(PROG_PATH,index_col='ppp_code',keep_default_na=True)

def read_json_file(file_path, keys_to_use):
    with open(file_path) as prog_output:
        content = json.load(prog_output)
     
    programming_result = content['result']['solution']
    records = []
    for prog in programming_result:
        records.append(get_record_from_json(prog,keys_to_use))        
        
    return tuple(records)

def get_record_from_json(json_record,keys_to_use):
    record = []
    matCodesAssigned=0
    for field in keys_to_use:
        if type(json_record[field]) is list:
            matCodesAssigned = int(json_record[field][0])
            record.append(json_record[field][0])
            if matCodesAssigned in df_mats.index:
                record.append(df_unique_mats.loc[matCodesAssigned]['matName'])
            else:
                record.append('NaN')
        else:
            record.append(json_record[field])
        
    return tuple(record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument("-f", "--file", help="Archivo de prediccion para analizar")
    args = parser.parse_args()

    if args.file:
        print('Input file to analize: ',args.file)
        JSON_INPUT_PATH = os.path.join('Request-files',args.file)
        position_filename = args.file.index('.')
        XLSX_OUTPUT_PATH = os.path.join('Output-files','prediction-'+args.file[0:position_filename]+'.xlsx')
        print('Output file: ',XLSX_OUTPUT_PATH)

        predictive_result = read_json_file(JSON_INPUT_PATH, KEYS_TO_USE)
        df_result = pd.DataFrame.from_records(predictive_result, columns=KEYS_TO_USE_IN_DF, index="pppCode")
        
        writer = pd.ExcelWriter(XLSX_OUTPUT_PATH, engine='xlsxwriter')
        df_result.to_excel(writer, sheet_name='Original Grid', index=True)

        df_result_with_reps = df_result
        df_result_with_reps["is_rep"] = np.nan
        df_result_films = df_result_with_reps.loc[df_result_with_reps.program=='FILM',:]

        for index, row in df_result_films.iterrows():
            if(np.isnan(df_result_films.at[index, 'is_rep'])):
                df_result_films.at[index, 'is_rep'] = 0
                start_date = row['profecha']
                end_date = pd.to_datetime(row['profecha'])
                end_date = end_date + pd.DateOffset(1)
                end_hour = row['hourFrom']
                mask = (df_result_films['profecha'] >= start_date) & (pd.to_datetime(df_result_films['profecha']) <= end_date) & (np.isnan(df_result_films['is_rep']) & (df_result_films['matCodesAssigned'] == row['matCodesAssigned']))
                for ipppCodeMat in df_result_films.loc[mask].index:
                    df_result_films.at[ipppCodeMat, 'is_rep'] = 1

        df_result_films.to_excel(writer, sheet_name='Films grids analysis')

        ds_count_unique = df_result.loc[df_result.program=='FILM',:].matName.value_counts()
        ds_count_unique.to_excel(writer, sheet_name='Count movies')
        
        df_result.loc[df_result.program=='FILM',:].groupby('profecha').avg_rating.agg(['count','min','max','mean']).to_excel(writer,sheet_name='Ratings by day')
        df_progs.groupby('mat_code')['rating'].agg(['count','min','max','mean']).to_excel(writer,sheet_name='Hstoric Materials')

        #Lista total de titulos
        mats_list = df_unique_mats.index.tolist()
        mats_set = set(mats_list)
        print('Total de materiales: ' + str(len(mats_set)))

        #Lista de titulos asignados
        mats_assigned_list = df_result.loc[df_result.program=='FILM',:].matCodesAssigned.tolist()
        #mats_assigned_list = df_result.matCodesAssigned.tolist()
        mats_assigned_set = set(mats_assigned_list)
        print('Total de materiales asignados: ' + str(len(mats_assigned_set)))

        mats_not_assigned = mats_set.difference(mats_assigned_set)
        print('Total de materiales NO asignados: ' + str(len(mats_not_assigned)))

        writer.save()