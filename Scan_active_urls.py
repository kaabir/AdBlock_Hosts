# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 12:43:46 2023

@author: NBMS1
"""
import asyncio
import httpx
import pandas as pd
from tqdm import tqdm
import nest_asyncio

nest_asyncio.apply()

# Function to read the CSV file
def read_hosts(file_path):
    try:
        df = pd.read_csv(file_path, sep='\t', header=None, names=['URL', 'Name'], encoding='utf-8')
        return df  # Do not add 'http://' here
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame(columns=['URL', 'Name'])

# Asynchronous function to check URL status
async def check_url(client, url):
    try:
        # Add 'http://' only temporarily when making the request
        response = await client.get(f'http://{url}', timeout=5.0)
        return url if response.status_code < 400 else None
    except (httpx.RequestError, httpx.HTTPStatusError):
        return None

# Main asynchronous function with concurrency control
async def main(urls, max_concurrent_tasks=100):
    active_urls = []
    sem = asyncio.Semaphore(max_concurrent_tasks)

    async with httpx.AsyncClient(timeout=5.0) as client:
        async def safe_check(url):
            async with sem:
                return await check_url(client, url)

        tasks = [safe_check(url) for url in urls]
        for result in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Checking URLs"):
            url = await result
            if url:
                active_urls.append(url)
                
    return active_urls

# Function to run async code
def run_async_checks(urls):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(main(urls))

if __name__ == "__main__":
    # Read the CSV file
    file_path = '/../'
    url_list = read_hosts(file_path + 'host.txt')

    if url_list.empty:
        print("No URLs to process. Exiting.")
    else:
        # Run the asynchronous checks
        active_urls = asyncio.run(main(url_list['URL']))

        # Save active URLs as a .txt file
        with open(file_path + 'Active_Hosts.txt', 'w') as f:
            for url in active_urls:
                f.write(f"{url}\n")
        
        # Optionally, save active URLs as a .csv file
        pd.DataFrame(active_urls, columns=['URL']).to_csv(file_path + 'Active_Hosts.csv', index=False, header=False)

        print(f"Found {len(active_urls)} active URLs out of {len(url_list)} total URLs.")
