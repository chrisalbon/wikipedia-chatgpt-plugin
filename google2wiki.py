# Import libraries
from typing import List
import requests
import bs4
import re


def get_wikipedia_article_urls(
    search_term: str, search_key: str, search_id: str
) -> List[str]:
    """
    This function takes a search term, google search api key, and google search engine id and returns a list of wikipedia article urls

    Parameters
    ----------
    search_term : str
        The search term
    search_key : str
        The google search api key
    search_id : str
        The google search engine id

    Returns
    -------
    article_urls : list
        A list of wikipedia article urls
    """
    # using the first page
    page = 1
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    # calculating start, (page=2) => (start=11), (page=3) => (start=21)
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={search_key}&cx={search_id}&q={search_term}&start={start}"

    # make the API request
    data = requests.get(url, timeout=100).json()

    # get the result items
    search_items = data.get("items")

    article_urls = []

    # iterate over 10 results found
    for _, search_item in enumerate(search_items, start=1):
        # extract the page url
        link = search_item.get("link")
        article_urls.append(link)

    return article_urls


def get_wikipedia_text_title_url(url: str, paragraph_number: int = 12) -> str:
    """
    This function takes a wikipedia url and returns the text of the first 3 paragraphs

    Parameters
    ----------
    url : str
        The wikipedia url
    paragraph_number : int
        The number of paragraphs to extract from the article

    Returns
    -------
    paragraph_number : str
        A string of the first 3 paragraphs of text

    """

    page = requests.get(url, timeout=100)
    soup = bs4.BeautifulSoup(page.content, "html.parser")

    pars = soup.select("div.mw-parser-output > p")
    non_empty_pars = [par.text.strip() for par in pars if par.text.strip()][
        :paragraph_number
    ]
    text = "\n".join(non_empty_pars)

    infobox = soup.select_one("table.infobox")
    if infobox:
        text = infobox.text.replace("\n", ", ")[:1000] + text

    # Regular expression pattern to match any number in brackets (i.e. [1], [2], [3], etc.)
    pattern = r"\[\d+\]"
    text = re.sub(pattern, "", text)

    try:
        title = soup.select("span.mw-page-title-main")[0].text
    except IndexError:
        # If an IndexError occurs, set the title to an empty string
        title = ""

    response = {"article_title": title, "article_text": text, "article_url": url}

    return response
