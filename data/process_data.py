import sys
import pandas as pd
import re
import numpy as np
from sqlalchemy import create_engine
import os


def load_data(messages_filepath, categories_filepath):
    """Read data using their raw files path and return result as DataFrame"""
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    return messages, categories

def clean_data(message_df, category_df):
    """Clean data to make it readable table"""
    category_df = pd.concat([category_df.drop(columns=['categories']) , category_df['categories'].str.split(';', expand=True)], axis=1)
    cat_cols = category_df.iloc[0,1:].values
    cat_cols = [col.split('-')[0] for col in cat_cols] 
    category_df.columns = ['id'] + cat_cols
    for col in cat_cols:
        category_df[col] = category_df[col].apply(lambda x: x.split('-')[1]).astype('int64')
    df = message_df.merge(category_df, how='left', left_on='id', right_on='id')
    # related columns contains 2 in which it shouldn't, we'll clean it to one
    df['related'] = np.where(df['related']==2, 1, df['related'])

    # There're some duplicated data, thus we'll eliminate it first
    df = df.drop_duplicates() 
    return df



def save_data(df, database_filename, table_name):
    """Export the cleaned data into a table in a database"""
    engine = create_engine(f'sqlite:///{database_filename}')
    df.to_sql(table_name, engine, index=False, if_exists='replace')
    pass 


def main():

    messages_filepath, categories_filepath, database_filepath = 'messages.csv','categories.csv','Disaster_response.db'
    table_name = 'response_message'

    print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
            .format(messages_filepath, categories_filepath))
    if os.path.exists(messages_filepath):
        

        message_df, category_df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(message_df, category_df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath, table_name)
        
        print('Cleaned data saved to database!')
    else:
        print("Please run this file on its directory. It use relative path thus, it can't find the data sources. \nPlease execute cd./data before running")
        exit()

if __name__ == '__main__':
    main()
