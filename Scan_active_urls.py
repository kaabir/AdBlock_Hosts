# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 12:43:46 2023

@author: NBMS1
"""

import httpx
import trio
import pandas as pd

df = 'C:/Users/NBMS1/Downloads/hosts.txt'

# Reading CSV
def read_Hosts(fil_Nam):
     with open(fil_Nam) as temp_fil:
         col_count = [ len(l.split(",")) for l in temp_fil.readlines() ]
         column_names = [j for j in range(0, max(col_count))]
         df = pd.DataFrame()
         df = pd.read_csv(fil_Nam, delimiter=",", names=column_names, header=None,index_col=None)
     return df
     df.clear()
     
url_List = read_Hosts(df)

url_List.columns =['URL','Name']
url_List['URL'] = 'http://' + url_List['URL'].astype(str)

Working_URLs = []


async def main(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response is not None:
                Working_URLs.append(url)
        except httpx.ConnectError:
            return False
        except httpx.ReadTimeout:
            return False
        except httpx.ReadError:
            return False
        except httpx.ConnectTimeout:
            return False
        except httpx.RemoteProtocolError:
            return False
            
            
# import pandas as pd
# #websites = pd.read_csv('C:/Users/NBMS1/Downloads/Most Popular websites.csv', index_col=0)
# websites = pd.read_csv('C:/Users/NBMS1/Downloads/websites.csv', header=None,index_col=None)
# websites.columns =['Name', 'URL', 'Rank']
# websites['URL'] = 'http://' + websites['URL'].astype(str)

for _, website in url_List.iterrows():
    trio.run(main,website['URL'])

pd.DataFrame(Working_URLs).to_excel('C:/Users/NBMS1/Downloads//Export_Hosts.xlsx')