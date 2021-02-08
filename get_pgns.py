#!/usr/bin/env python3

'''
A helpful scraper to tear down a bunch of PGN files
to be used as the data set for training
our model.

Last write
user: j-a-collins
date: 08-02-21
'''

# # # Imports
import requests  
from bs4 import BeautifulSoup

# # # Relevant URL
archive_url = "https://www.pgnmentor.com/files.html"


def get_file_links():
    '''
    Creates a Soup object, finds all links on the pages
    then filters the links by extension - in this case,
    we find all the .pgn files
    '''
    response = requests.get(archive_url)
    soup = BeautifulSoup(response.content, 'html5lib')
    links = soup.findAll('a')
    file_links = [archive_url + link['href'] 
    for link in links if link['href'].endswith('pgn')]

    return file_links  
                                                        
                                                        
def download_files(file_links):  
    '''
    Iterates through all the links in file_links
    and then downloads them one at a time.
    '''
    for link in file_links:  
        # obtain filename by splitting url and getting  
        # last string  
        file_name = link.split('/')[-1]  
        print(f"Downloading: {file_name}") 

        response = requests.get(link, stream = True)  
          
        # download started  
        with open(file_name, 'wb') as file:  
            for chunk in response.iter_content(chunk_size = 1024 * 1024):  
                if chunk:  
                    file.write(chunk)  
          
        print(f"Downloaded: {file_name}") 
  
    print ("All files downloaded!") 
    return


if __name__ == "__main__":  
    file_links = get_file_links()  
    download_files(file_links)  
