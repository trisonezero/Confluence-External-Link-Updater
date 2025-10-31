# Confluence-External-Link-Updater
Searchs and replaces broken external links on confluence using confluence API

https://atlassian-python-api.readthedocs.io/

I was tasked with replacing broken links on our departmenet confluence during my internship. After some googling I found there is no free confluence function for this when hosting confluence on cloud, and API seems to be the most effective solution.

# Methodology
1. API call to retrieve list of all pages in space
2. For each page use beautifulsoup to parse html, retrieve all links with class external link
3. For each link determine if it leads to our old domain or if broken based on requests status code
4. Save results as csv
5. Manually go through csv and find corrected links
6. Use the second program to auto update all links with the newly updated csv
