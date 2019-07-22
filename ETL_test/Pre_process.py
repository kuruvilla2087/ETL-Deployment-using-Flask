import sys
import pandas as pd
import numpy as np
import phonenumbers
import os
from flask import Flask
from email_validator import validate_email, EmailNotValidError


from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
    region_code_for_number,
)

#Value for Output
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)


#Function to Validate email as Emails are not Correct
def valid_email(email):
    try:
        v = validate_email(email)  # validate and get info
        email = v["email"]  # replace with normalized form
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        return(str('Email not Valid'))
    return(str('Email Valid'))


#Function for Phone Number Colum Creation
def mobile(x):
    res = x.split(",")
    return {"phone_type":"mobile","phone_number":res}

extension = '.csv'

#Function to Csv files from Path
def read_csv(path_name):
    if os.path.exists(path_name):
        try:
            files = [file_name for file_name in os.listdir(path_name) if extension in file_name]
            df = [pd.read_csv(file_name) for file_name in files]
        except Exception as e:
            print('There was an issue in file .Please check')
        return df

# dict for Gender Mapping
gender_mapping = {0 : 'M',1: 'F'}


# # # Output File creation
def etl_preprocess(File1,File2):
    try:
        #Pre - Processing Columns

        #Remotving Spaces from email Column
        File1['email'] = File1['email'].replace(' ', '', regex=True)
        # checking if Email is Valid
        File1['email_valid_check'] =  File1['email'].apply(valid_email)

        File2['attr1'] = File2.attr1.astype(str).str.lower()
        #Mapping Gender column to Male(M) and Female(F)
        File2['gender'] = File2['sex'].map(gender_mapping)

        #Merging both Datasets to get by id (i.e Referral code)
        df_temp = pd.merge(File2.loc[:, ['id', 'sex', 'tier', 'attr1', 'attr2','gender']], File1.iloc[:, 0:7], on=['id'],
                                how='left')
        #Tranforming Dataframes
        df_temp['external_id'] = df_temp.apply(lambda row: row['email'] if row['email'] else 'NA', axis=1)
        df_temp['opted_in'] = df_temp['tier'].apply(lambda x: 'True' if not x else 'False')
        df_temp['external_id_type'] = df_temp['tier']
        pn = df_temp['attr2'].apply(phonenumbers.parse)
        for i in pn:
            df_temp['locale'] = region_code_for_country_code(i.country_code)
        df_temp['ip'] = ''
        df_temp['dob'] = ''
        df_temp['address'] = ''
        df_temp['city'] = df_temp['locale']
        df_temp['state'] = ''
        df_temp['zip'] = ''
        df_temp['country'] = ''
        df_temp['referral'] = df_temp['id']
        df_temp["phone_numbers"] = File2["attr2"].apply(lambda x: mobile(x))


        #Selecting columns
        df_temp = df_temp[['external_id', 'opted_in', 'external_id_type', 'email', 'locale','ip','dob','address','city','state',
                             'zip','country','gender','first_name','last_name','referral','phone_numbers','email_valid_check']]

        # Removing Nan and replacing by blanks
        df_temp.replace(np.nan, '', inplace=True)

        #Copying Columns from staging Table df_temp
        df_final = pd.DataFrame(columns=df_temp.columns)

        #Inserting into final Table
        df_final = df_final.append(df_temp, ignore_index=True)

    except Exception as e:
        print('there was an error with your input :{0}'.format(e))
    return df_final

