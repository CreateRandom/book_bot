import config.apiKeys as apiKeys
import urllib
from utils.webHelpers import get_json_from_url

googleKey = apiKeys.keys['googleBooks']['key']
googleBooksURL = "https://www.googleapis.com/books/v1/" # volumes/zyTCAlFPjgYC?projection=lite&key=yourAPIKey"  # NOQA
sampleSearch = "https://www.googleapis.com/books/v1/volumes?q=flowers+inauthor:keyes&key=yourAPIKey"  # NOQA


def getVolumeInformation(volumeId, projection="lite"):
    url = googleBooksURL + "volumes/" + volumeId + "?projection=" + \
        projection + "&key=" + googleKey
    return get_json_from_url(url)


# does a Google Books search based on an approximate name and an
# approximate author if known and returns the first item found
def identifyBook(approxName, approxAuthor=None):
    items = getSearchResults(approxName,approxAuthor)
    if len(items) > 0:
        result = items[0]
    else:
        result = None
    return result


def getSearchResults(query, author=None):
    # https://www.googleapis.com/books/v1/volumes?q=flowers+inauthor:keyes&key=AIzaSyCcF4oL9AwBtPHV5nU1RQIELNBZ63lfsaA

    query = urllib.parse.quote(query)
    url = googleBooksURL + "volumes?q=" + query

    if author is not None:
        url = url + "+inauthor:" + author

    url = url + "&key=" + googleKey
    full_list = get_json_from_url(url)
    items = []
    if "items" in full_list:
        # list of dicts
        items = full_list["items"]

    return items
