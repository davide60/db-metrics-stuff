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
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(f"{dname}/")
config='C:/Users/david olivari/Projects/python/cfgs/dbs.cfg'

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler=logging.FileHandler(f'{os.path.basename(__file__)}.log')
formatter=logging.Formatter('%(levelname)s : %(message)s')
gen_err_formatter =  logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)s] %(message)s")   
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info(f"Start of script {datetime.now().strftime('%a ,%d %b %H:%M:%S')}")


@click.command()
@click.option('--tns'  , '-t' , prompt=True )
def main(tns):
    try:
        dbData = configparser.ConfigParser()
        dbData.read(config)
        username = 'system'
        password = dbData.get(tns.upper(),f'password_{username}')
        conn = cx_Oracle.connect(username,password,tns.upper())
        logger.info(f"Connected to {tns}")
        sql=open('pySQL/visual/load_curves.sql').read()
        data_df=pd.read_sql(sql,conn,index_col='SAMPLE_TIME')
        # if RAC multiply all values by 2, or whatever #in cluster
        cur=conn.cursor()
        RAC=cur.execute("select value from v$parameter where name='cluster_database'").fetchone()[0]
        cur.close()
        if RAC == 'TRUE':
            multiplier = 2
        else:
            multiplier = 1
        logger.info(f"multiplier set to {multiplier}")
        user_stats_df = data_df[['CPU',
                                 'UIO',
                                 'CONCURRENCY',
                                 'APPLICATION',
                                 'CLUST',
                                 'NETWORK','QUEUEING','OTHER']].multiply(multiplier)
        user_stats_df.plot.area(figsize=(10,6),
                                title=f"{tns} load",
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
        plt.savefig(f'{tns.upper()}_load.png')
    except Exception as e:
        print ( f"Program failed with {e}")
        sys.exit(1)
        
main()
sys.exit(0)