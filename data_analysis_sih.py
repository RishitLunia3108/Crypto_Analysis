'''
Transaction History:
Number of transactions: Analyze the total number of transactions associated with an account. 
Malicious accounts might have an unusually high number of transactions.
Transaction frequency: Look at how often transactions occur. Malicious accounts might have 
irregular patterns, such as sudden spikes or long periods of inactivity.
Transaction amount: Consider the average transaction amount and whether there are transactions 
with extremely high or low values.

Sender and Receiver Analysis:
Reputation of counterparties: Analyze the reputation of the sender and receiver accounts. Known 
malicious accounts or addresses can be flagged.
Number of counterparties: Evaluate how many different counterparties an account interacts with. Malicious accounts may interact with a wide range of accounts to obfuscate their activities.

Timestamp and Time-based Features:
Transaction timestamp: Consider the time and date of transactions. Detect unusual transaction 
times, such as transactions happening only during certain hours or days.----NO
Time since last transaction: Calculate the time gap between transactions. Malicious accounts may 
exhibit irregular transaction patterns.

Network Graph Features:
Network analysis: Construct a graph of account interactions and analyze network properties such 
as centrality, clustering coefficient, and degree distribution. ----GRAPH CREATED IN 
KNOWLEDGE GRAPH AND I DON'T KNOW HOW TO DO THE SECOND PART
Anomaly detection: Apply graph-based anomaly detection algorithms to identify accounts with 
unusual connectivity patterns.----SAME AS ABOVE

Blockchain-Specific Features:
Smart contract interactions: Analyze whether an account interacts with smart contracts and the 
types of contracts involved.---NO INFO ABOUT SMART CONTRACT AVAILABLE
Gas consumption: Consider the amount of gas consumed by transactions. Unusually high gas 
consumption can be a sign of malicious activities.
'''

import requests
import mysql.connector as m
import pandas as pd
import numpy as np

score=0

'''
data=requests.get('https://blockchain.info/rawaddr/bc1q7scj57g7m6w6a3hx8h4vvd47nj0yr063f3n3yu')
d=data.json()
'''

import json
fo=open('wallet6_data.json','r')
d=json.load(fo)
fo.close()

wallet=d['address']

mo=m.connect(host='localhost',user='root',password='reha',database='sih_analysis_db')
co=mo.cursor()
co.execute('use sih_analysis_db')
co.execute('select sd from common_data')
sd=co.fetchone()[0]
co.execute('select mean from common_data')
mean=co.fetchone()[0]
co.execute('select max_no_transactions from common_data')
max_v=co.fetchone()[0]

#checking total number of transactions
if d['n_tx']>(mean+sd):
    score+=((d['n_tx']-(mean+sd))/max_v)*10

#checking transaction frequency
timevamt=[]
time=[]
amt=[]
interacted_with_wallets=[]
interacted_with_wallets_d={}
gas_list=[]
for i in d['txs']:
    time.append(i['time'])
    timevamt.append([i['time'],i['result']])
    amt.append(i['result'])
    for j in i['inputs']:
        if j['prev_out']['addr'] not in interacted_with_wallets and j['prev_out']['addr']!=wallet:
            interacted_with_wallets.append(j['prev_out']['addr'])
            interacted_with_wallets_d[j['prev_out']['addr']]=[1,0]
        elif j['prev_out']['addr']!=wallet:
            interacted_with_wallets_d[j['prev_out']['addr']][0]+=1
    for j in i['out']:
        if j['addr'] not in interacted_with_wallets and j['addr']!=wallet:
            interacted_with_wallets.append(j['addr'])
            interacted_with_wallets_d[j['addr']]=[0,1]
        elif j['addr']!=wallet:
            interacted_with_wallets_d[j['addr']][1]+=1
    gas_list.append(i['fee'])
#issue with getting number of transcations per unit time - what unit to take mainly

#checking transaction amounts
amt_series=pd.Series(amt)
q1 = np.quantile(amt_series, 0.25)
q3 = np.quantile(amt_series, 0.75)
iqr = q3-q1
upper_bound = q3+(1.5*iqr)
outliers = amt_series[(amt_series >= upper_bound)]
score+=outliers.size

#checking reputation of counterparties
co.execute('select walleet_id from wallet_score')
all_wallets=co.fetchall()
for i in range(len(all_wallets)):
    all_wallets[i]= all_wallets[i][0]
co.execute('select score from wallet_score')
all_scores=co.fetchall()
for i in range(len(all_scores)):
    all_scores[i]= all_scores[i][0]
for i in interacted_with_wallets:
    if i in all_wallets:
        if all_scores[all_wallets.index(i)]>7:
            score+=1

#checking number of counterparties
single_int=0
for i in interacted_with_wallets_d:
    if interacted_with_wallets_d[i]==[0,1] or interacted_with_wallets_d[i]==[1,0] or interacted_with_wallets_d[i]==[1,1]:
        single_int+=1
score+=single_int*single_int*2/len(interacted_with_wallets)

#checking gap between transactions
time_sorted=time[:]
time_sorted.sort()
if len(time_sorted)>1:
    time_gaps=[]
    for i in range(len(time_sorted)-1):
        time_gaps.append(time_sorted[i+1]-time_sorted[i])
    timegap_series=pd.Series(time_gaps)
    q1 = np.quantile(timegap_series, 0.25)
    q3 = np.quantile(timegap_series, 0.75)
    iqr = q3-q1
    upper_bound = q3+(1.5*iqr)
    lower_bound = q1-(1.5*iqr)
    outliers = timegap_series[(timegap_series >= upper_bound)|(timegap_series <= lower_bound)]
    score+=outliers.size

#checking gas consumption
co.execute('select threshold_gas from common_data')
th_gas=co.fetchone()[0]
for i in gas_list:
    if i>th_gas:
        score+=1

if str(wallet) not in all_wallets:
    co.execute('insert into wallet_score values(%s,%s)',(wallet,score))
    mo.commit()
else:
    co.execute('update wallet_score set score=%s where walleet_id=%s',(score,wallet))
    mo.commit()

'''
Machine Learning Models:----NO
Use supervised learning algorithms (e.g., decision trees, random forests, gradient boosting, 
neural networks) to train a classification model with labeled data (malicious vs. non-malicious 
accounts).
Feature selection: Employ techniques like feature selection to identify the most relevant 
features for classification.
Unsupervised learning: Consider unsupervised learning techniques, such as clustering, to group 
accounts with similar behaviors.

Historical Data:----NO
Use historical blockchn data to create a time series of features, enabling the model to capture 
evolving behavior patterns.

External Data Sources:-----NO
Incorporate external data sources, such as known blacklisted addresses or information from threat 
intelligence feeds, to enhance the model's accuracy.

Behavioral Patterns:-----HOW?
Identify behavioral patterns associated with known malicious accounts, such as pump-and-dump 
schemes, Ponzi schemes, or phishing attacks.

Validation and Testing:-----eh.
Implement robust cross-validation and testing procedures to ensure the model's effectiveness and 
generalizability.
'''
