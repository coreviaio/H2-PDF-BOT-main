from bs4 import BeautifulSoup, Comment
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from urllib.parse import urlparse


import re
# import requests
# from bs4 import BeautifulSoup

def get_pubmed_article_id(title: str, doi: str = None):
    """
    Return PubMed IDs for an article title using NCBI's structured API.
    """
    try:
        if not title or not title.strip():
            return []

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        headers = {
            "User-Agent": "flask-pdf-bot/1.0 (PMID lookup)"
        }

        search_terms = []
        if doi and doi.strip():
            search_terms.append(f'"{doi.strip()}"[AID]')
        search_terms.extend([
            f'"{title.strip()}"[Title]',
            f'{title.strip()}[Title]',
        ])

        for term in search_terms:
            response = requests.get(
                base_url,
                params={
                    "db": "pubmed",
                    "term": term,
                    "retmode": "json",
                    "retmax": 5,
                },
                headers=headers,
                timeout=15,
            )
            if response.status_code != 200:
                raise Exception(
                    f"Failed to fetch data from PubMed. HTTP status code: {response.status_code}"
                )

            result = response.json()
            pmids = [
                pmid
                for pmid in result.get("esearchresult", {}).get("idlist", [])
                if pmid.isdigit()
            ]
            if pmids:
                return pmids

        return []

    except Exception as e:
        print("Exception in get_pubmed_article_id: ", e)
        return []



def driver_wait(driver,source=None):
    time.sleep(9)
    # if source == 'www.sciencedirect.com':
    #     WebDriverWait(driver, 5).until(
    #         EC.presence_of_element_located((By.TAG_NAME, "article"))
    #     )

    # elif source == "www.ingentaconnect.com":
    #     time.sleep(3)
    # elif source == "adsabs.harvard.edu":
    #     time.sleep(1)
    # else:
    #     time.sleep(3)




# this function is used to fetch the scimago's website search page and then call another function to fetch the quartile, impact_factor, h-index,  of the journal
def fetch_scimago_search(journal_name):
    # print("Journal Name: ",journal_name)
    try:
        url = f"https://www.scimagojr.com/journalsearch.php?q={journal_name}&tip=sid&clean=0"
        url2 = "https://www.scimagojr.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from Scimago. HTTP status code: {response.status_code}")
                
        soup = BeautifulSoup(response.text, 'html.parser')
        # with open("scimago_search.html",'w') as f:
        #     f.write(str(soup))

        # checks if the page has no results
        no_results = soup.find(string="Sorry, no results were found.")
        if no_results:
            # print("No results found on the Scimago page.")
            return None, None, None
        
        rank = soup.find("div", {"class": "search_results"})
        

        if rank:
            # Remove comments by extracting all comments and ensuring 'a' is not in them
            comments = rank.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            
            # Loop through all 'a' elements inside the rank element
            for a_tag in rank.find_all('a'):
                # Check if the 'a' element contains a 'span' with class 'jrnlname' and matches the journal_name
                jrnlname_span = a_tag.find('span', {'class': 'jrnlname'})
                # print("jrnlname_span.strip.text: ",jrnlname_span.text.strip())
                # print("jrnlname_span: ",jrnlname_span)
                if jrnlname_span and jrnlname_span.text.strip() == journal_name:
                    href = a_tag.get('href')  # Get the href attribute
                    url2 = url2 + href
                    ranking = get_scimago_quartile(url2)  # Assume this function is already defined
                    return ranking
            
            # If no exact match found, proceed with the previous logic
            first_a = rank.find('a')
            if first_a:
                href = first_a.get('href')  # Get the href attribute
                url2 = url2 + href
                ranking = get_scimago_quartile(url2)
                return ranking
            else:
                print("No <a> element found.")
                return None, None, None
        else:
            print("No rank element found.")
            return  None, None, None
    except Exception as e:
        print("Exception in get_scimago_search: ",e)
        return None, None, None
    


# this function is used to fetch the quartile of the journal page

def get_scimago_quartile(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to fetch data from Scimago. HTTP status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        
        ## Get the last impact factor, and h-index from the same html content
        impact_factor = get_last_impact_factor(response.text)
        h_index = get_h_index(response.text)

        ## get the last quartile: 
        # Find the cellcontent div
        cellcontent_div = soup.find("div", {"class": "cellcontent"})
        if not cellcontent_div:
            print("Unable to find the cellcontent div in the page.")
        
        # Find the table within the cellcontent div
        table = cellcontent_div.find("table")
        if not table:
            print("Unable to find the table in the cellcontent div.")
        
        # Get the last row of the table
        last_row = table.find_all("tr")[-1]
        
        # Get the last cell (Quartile) from the last row
        last_quartile = last_row.find_all("td")[-1].text.strip()
        
        # print("Last Quartile value:", last_quartile)
        return last_quartile,impact_factor ,h_index
    
    except Exception as e:
        print("Exception in fetch_scimago_quartile:", e)
        return None, None, None



def get_last_impact_factor(html_content):
    """
    Fetch the last "Cites / Doc. (2 years)" value from the given HTML content.

    Args:
        html_content (str): The HTML content as a string.

    Returns:
        float: The last impact factor found, or None if not found.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the target div by its class
        target_div = soup.find('div', class_='cell1x2 dynamiccell')
        if not target_div:
            return None
            return None

        # Find all rows in the table
        rows = target_div.find_all('tr')

        # Extract the last row with "Cites / Doc. (2 years)" text
        for row in reversed(rows):
            cells = row.find_all('td')
            if len(cells) == 3 and cells[0].get_text(strip=True) == "Cites / Doc. (2 years)":
                return float(cells[2].get_text(strip=True))

        return None  # Return None if no match found

    except Exception as e:
        print(f"Error parsing HTML in get_last_impact_factor: {e}")
        return None

# this function is used to fetch the h-index of the journal from sciMago's journal's html content
def get_h_index(html_text):
    """
    Extracts the H-Index value from the HTML response.

    Args:
        html_text (str): The HTML content as a string.

    Returns:
        int: The H-Index value found.
    """
    soup = BeautifulSoup(html_text, 'html.parser')

    # Print the parsed HTML to debug
    # print(soup.prettify())  # This will show you the structured HTML, and you can inspect the divs

    # Locate the H-Index section by finding the <h2> with text 'H-Index'
    h_index_heading = soup.find('h2', string='H-Index')
    if not h_index_heading:
        raise ValueError("H-Index heading not found.")

    # Find the <p> tag with the class 'hindexnumber' following the heading
    h_index_number = h_index_heading.find_next('p', class_='hindexnumber')
    if not h_index_number:
        return None

    try:
        return int(h_index_number.text.strip())
    except ValueError:
        print("Failed to parse H-Index value.")
        return None
