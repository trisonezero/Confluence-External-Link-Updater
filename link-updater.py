from atlassian import Confluence
import pandas as pd
import urllib3
from tqdm import tqdm
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

confluence = Confluence(
    url='https://confluence.domain/wiki',
    # @domain.com email
    username='username@domain.com',
    # Api token linked to domain email
    password='API Token',
    verify_ssl=False,
    cloud = True
)

def update_links(csv_loc):
    df = pd.read_csv(csv_loc)

    # Divide links by page, for each page update links
    df_page = df.groupby('Page ID')
    
    for page_id, page in tqdm(df_page):
        print(page_id)
        try:
            page_details = confluence.get_page_by_id(page_id, status='current', expand='body.view')
        except:
            print('Page ' + str(page_id) + ' Not Found')
            continue

        # Based on what was filled in Correct Link Column execute the corresponing operation
        updated_body = page_details['body']['view']['value']
        for i, link in page.iterrows():
            match link['Correct Link']:
                case 'STRIKETHROUGH':
                    updated_body = updated_body.replace(link['Link Text'], '<del>' + link['Link Text'] + '</del>')

                case 'IGNORE':
                    pass

                case _:
                    updated_body = updated_body.replace(link['Link URL'], link['Correct Link'])
        confluence.update_page(page_id=page_id, title=page['Page Title'].iloc[0], body = updated_body, version_comment='Update test')

def main():
    csv_loc = 'filename.csv'
    update_links(csv_loc)


if __name__ == '__main__':
    main()

    