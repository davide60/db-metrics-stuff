#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:06:08 2021

@author: David Olivari
"""

import sys
import configparser
import click
import os
from datetime import datetime
#import multiprocessing as mp
import logging
import pandas as pd
import cx_Oracle
import matplotlib.pyplot as plt
import glob
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(f"{dname}/")
config='C:/Users/david olivari/Projects/python/cfgs/dbs.cfg'
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
base=os.path.basename(__file__)
file_handler=logging.FileHandler(f'logs/{os.path.splitext(base)[0]}.log')
formatter=logging.Formatter('%(levelname)s : %(message)s')
gen_err_formatter =  logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)s] %(message)s")   
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info(f"Start of script {datetime.now().strftime('%a ,%d %b %H:%M:%S')}")
now=datetime.now()

csv_store='data'
def plotData (tns,instance_number):
    dataframe = pd.read_csv(f'{csv_store}/{tns}_combined.csv',index_col='SAMPLE_TIME')
    dataframe.plot.area(figsize=(10,6),
                        title=f'{tns},inst:{instance_number}, load on: {now.strftime("%a, %d %b %y, %H:%M")}',
                        grid=True,
                        color={'CPU' :'green', 
                               'UIO' : 'blue',
                               'CONCURRENCY':'#790000',
                               'APPLICATION':'red',
                               'CLUST':'#BEBEBE',
                               'NETWORK':'#cc9900' ,
                               'QUEUEING':'#D3D3D3',
                               'OTHER':'pink'},
                        use_index=True).legend(loc='upper left')
    plt.margins(tight=True)
    plt.rc_context({'axes.autolimit_mode': 'round_numbers'})
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig(f'{tns}_load.png')    
    plt.show()

def buildDF(tns):
    all_files = glob.glob(f"{csv_store}/{tns}_*.csv")
    #first, maybe only one file
    data = pd.read_csv(all_files[0],header=0,sep=',',index_col='SAMPLE_TIME')
    i =1 
    while i < len(all_files):
        data=data.append(pd.read_csv(all_files[i],header=0,index_col='SAMPLE_TIME'))
        i=i+1
        
    #data.drop_duplicates(keep = 'last' , inplace = True)
    data = data[~data.index.duplicated(keep='first')]
    data.sort_index(inplace=True)
    data.to_csv(f'{csv_store}/{tns}_combined.csv',index=True)
    return data

@click.command()
@click.option('--tns'  , '-t' , prompt=True )
@click.option('--plot'  , '-p' ,is_flag=True, help="Produce Plot of Load Chart")
def main(tns,plot):
    try:
        tns=tns.upper()
        dbData = configparser.ConfigParser()
        dbData.read(config)
        username = 'system'
        password = dbData.get(tns,f'password_{username}')
        conn = cx_Oracle.connect(username,password,tns)
        logger.info(f"Connected to {tns}")
        # if RAC multiply all values by 2, or whatever #in cluster
        cur=conn.cursor()
        RAC=cur.execute("select value from v$parameter where name='cluster_database'").fetchone()[0]
        instance_number = cur.execute("select instance_number from v$instance").fetchone()[0]
        cur.close()
        if not plot:
            sql=open('pySQL/visual/load_curves.sql').read()
            data_df=pd.read_sql(sql,conn,index_col='SAMPLE_TIME')
            if RAC == 'TRUE':
                multiplier = 2
            else:
                multiplier = 1
            logger.info(f"multiplier set to {multiplier}")
            ts = now.strftime("%y%m%d_%H%M%S")
            user_stats_df = data_df[['CPU',
                                     'UIO',
                                     'CONCURRENCY',
                                     'APPLICATION',
                                     'CLUST',
                                     'NETWORK','QUEUEING','OTHER']].multiply(multiplier)
            user_stats_df.to_csv(f'{csv_store}/{tns}_{ts}.csv',index=True)
            logger.info(f"CSV {csv_store}/{tns}_{ts}.csv written")
            buildDF(tns)
            end = datetime.now()
            logger.info(f"Combined CSV {csv_store}/{tns}_combined.csv written")
            logger.info(f"Script Duration:{end-now}")
        else:
            logger.info(f"Producing Plot for {tns}")
            plotData(tns,instance_number)
    except Exception as e:
        logger.error ( f"Program failed in mains with {e}")
        sys.exit(1)
       
main()
sys.exit(0)