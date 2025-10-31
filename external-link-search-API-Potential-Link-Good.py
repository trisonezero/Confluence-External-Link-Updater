from atlassian import Confluence
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

domain = 'https://confluence.domain/wiki'
confluence = Confluence(
    url=domain,
    # @domain.com email
    username='username@domain.com',
    # Api token linked to email
    password='API Token',
    verify_ssl=False,
    cloud = True
)

# Given list of external links in dict format returned from get_links_space, get potential correct links via CQL fuzzy search API call
# Optional as this is an expensive operation and does not always return results as page titles change extensively
def get_potential_links(links):
    for link in links:
        url_title = link['Link URL'].split('/')[-1].replace('+', ' ')

        cql = f'''
        type = page
        and title ~ "{url_title}"
        '''
        # Search for max 3 potential correct links based on page title contained within URL
        c = confluence.cql(cql, start=0, limit=3)
        potential_links = [domain + page['url'] for page in c['results']]


        link['Potential Correct Link'] = potential_links

# Given page details in json format, retrieve valid external links
def get_links_page(page):
    links = BeautifulSoup(page['body']['view']['value'], 'html.parser').find_all('a', {'class': 'external-link'})

    external_links = []
    for link in links:
            href = link.get('href')
            
            # Only retrieves links that lead to old confluence domain
            if 'confluence' in href:

                l = {'Page Link': domain + page['_links']['webui'], 
                     'Page Title': page['title'], 
                     'Page ID': page['id'], 
                     'Last Updated': page['history']['lastUpdated']['when'], 
                     'Link Text': link.text, 
                     'Link URL': link.get('href'), 
                     'Reason': "Old Domain"
                    }

            # External Links that do not lead to old confluence domain
            else:
                l = {'Page Link': url + page['_links']['webui'], 
                     'Page Title': page['title'], 
                     'Page ID': page['id'], 
                     'Last Updated': page['history']['lastUpdated']['when'], 
                     'Link Text': link.text, 
                     'Link URL': link.get('href'), 
                    }
                
                # Check if link is broken via requests, only keep unsuccessful links
                response = requests.get(l['Link URL'], timeout=10)
                if response.status_code <= 199 or response.status_code >= 400:
                    l['Reason'] = response.status_code
                    external_links.append(l)
                       
    return external_links

# Save list of external links in dict format as csv
def to_csv(dict, title):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_datetime = datetime.now().strftime("%Y%m%d")

    filename = f"{title}-{current_datetime}.csv"
    filepath = os.path.join(script_dir, filename)

    df = pd.DataFrame(dict)
    df.to_csv(filepath, mode='w', index=False)

# Get all external links for each page in a space given space key
def get_links_space(space_key):

    # Exclude page if page title contains any of the following keywords
    keywords = ['RETIRE', 'ARCHIVE', 'MEETING', 'SUPPORT SYNC', 'RETIRED', 'MONITORING COE', 'TOWNHALL', 'READINESS']

    
    # API call to retrieve all pages
    all_pages = confluence.get_all_pages_from_space(space_key, start=0, limit=100, status=None, expand='body.view,history.lastUpdated', content_type='page')

    links = []
    for page in all_pages:
        year = datetime.fromisoformat(page['history']['lastUpdated']['when']).year

        # Last updated year must be greater equal to x
        if  year >= 2022 and not any(keyword in page['title'].upper() for keyword in keywords):
            links+=(get_links_page(page))
    return links

def main():
    space_key = '~spacekey'
    links = get_links_space(space_key)
    # get_potential_links(links)
    to_csv(links, space_key)
    print('CSV Created')


if __name__ == '__main__':
    main()

    