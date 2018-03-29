import utils.booksApi as booksApi
import utils.goodreadsApi as goodreadsApi
# att_sources dicts:
# specify the fields an entity can have as well as a list of sources
# attributes and sources (source = one particular API call)
book_att_sources = {
    'approxName': ['user'],
    'approxAuthor': ['user'],
    # scrape the ISBN from Google Books
    'isbn_10': ['gBooks_volume'],
    'isbn_13': ['gBooks_volume'],
    # there might be multiple authors, this attribute is a dict [0, ..n --> name]
    'authors': ['gBooks_volume'],
    'gBooksVolumeId': ['gBooks_volume'],
    'title': ['gBooks_volume'],
    'summary': ['gBooks_volume'],
    'price': ['gBooks_volume'],
    'pageCount': ['gBook_volume'],
    'ratings': ['goodreads_ratings'],
    'reviews': ['goodreads_reviews']

}

# attributes and sources
authors_att_sources = {
    'approxName': ['user'],
    'goodreadsAuthorId': ['goodreads_author_ID'],
    'worksAuthored': ['goodreads_works_authored'],

}
# types of objects and specifications for each of them
object_types = {
    'book': book_att_sources,
    'author': authors_att_sources
}

def getGoodreadsAuthorID(authorObject):
    name = authorObject.att_dict['approxName']
    id = goodreadsApi.get_author_id(name)

    if id is not None:
        authorObject.att_dict['goodreadsAuthorId'] = id
        return True

    return False


def getWorksAuthored(authorObject):

    # make sure we have an author id, so scrape that first
    found, authorObject = scrapeAttributes(authorObject,['goodreadsAuthorId'])

    if found['goodreadsAuthorId']:
        id = authorObject.att_dict['goodreadsAuthorId']
        books = goodreadsApi.get_authors_books(id)
        if books is not None:
            authorObject.att_dict['worksAuthored'] = books
            return True

    return False

def getRatings(bookObject):
    # make sure we have an ISBN present
    isbn = checkISBN(bookObject)

    if isbn is not None:
        # a dict with rating information
        ratings = goodreadsApi.get_review_stats(isbn)
        if ratings is not None:
            bookObject.att_dict['ratings'] = ratings
            return True

    return False

def getReviews(bookObject):
    # make sure we have an ISBN present
    isbn = checkISBN(bookObject)

    if isbn is not None:
        reviews = goodreadsApi.get_reviews(isbn)
        if reviews is not None:
            bookObject.att_dict['reviews'] = reviews
            return True

    return False


# checks for presence of an ISBN and returns it if present
def checkISBN(bookObject):
    # make sure we have some ISBN, so scrape that first
    found, bookObject = scrapeAttributes(bookObject, ['isbn_13', 'isbn_10'])
    isbn = None
    if found['isbn_13']:
        isbn = bookObject.att_dict['isbn_13']
    # fallback
    elif found['isbn_10']:
        isbn = bookObject.att_dict['isbn_10']

    return isbn

# our attribute names : fields in the volume info
gBooksVolume = {
    # isbn information, pretty essential for finding a book
    'isbn_10':'[\'volumeInfo\'][\'industryIdentifiers\'][0][\'identifier\']',
    'isbn_13': '[\'volumeInfo\'][\'industryIdentifiers\'][1][\'identifier\']',

    # list of authors
    'authors': '[\'volumeInfo\'][\'authors\']',
    'gBooksVolumeId': ' [\'id\'] ',
    'title': '[\'volumeInfo\'][\'title\']',
    'summary': '[\'volumeInfo\'][\'description\']',
    'price': '[\'saleInfo\'][\'listPrice\'][\'amount\']',
    'pageCount': '[\'volumeInfo\'][\'readingModes\'][\'pageCount\']'
}

def getBooksVolume(bookObject):
    if 'gBooksVolumeId' not in bookObject.att_dict:
        raise ValueError('Entity needs to be a book!')
    volumeId = bookObject.att_dict['gBooksVolumeId']
    info = None
    # do a search and get the full books#volume based on the approxName and the approxAuthor
    if volumeId is None:
        info = booksApi.identifyBook(bookObject.att_dict['approxName'],
                                     bookObject.att_dict['approxAuthor'])
    else:
        info = booksApi.getVolumeInformation(volumeId)
    # if we didn't find anything, flag this up
    if info is None:
        return False
    else:
        parseBooksVolume(bookObject, info)
        return True


def parseBooksVolume(bookObject, info):
    for entry in bookObject.att_dict:
        # if we can extract this and still need it
        if 'gBooks_volume' in book_att_sources[entry] and bookObject.att_dict[entry] is None:  # NOQA
            field_to_extract = gBooksVolume[entry]
            # build the extraction call dynamically based on the field to extract
            expression = "info" + field_to_extract
            try:
                # make the extraction call
                value_to_fill = eval(expression)
                # store the value we found
                bookObject.att_dict[entry] = value_to_fill
            except:
                # bad luck, didn't find anything
                print(expression + ' failed.')


# a mapping between source calls and functions
source_call_dict = {
    'gBooks_volume': getBooksVolume,
    'goodreads_author_ID': getGoodreadsAuthorID,
    'goodreads_works_authored': getWorksAuthored,
    'goodreads_ratings': getRatings,
    'goodreads_reviews': getReviews,
}


class objectInfo(object):
    def __init__(self, object_type, init_values=None):
        super().__init__()
        # get the object type and then its key set, i.e. its attributes as a
        # list
        self.init_empty_dict(object_types[object_type].keys())
        self.type = object_type
        if init_values is not None:
            # set initial values
            for key in init_values:
                self.att_dict[key] = init_values[key]

    def init_empty_dict(self, attribute_list):
        # empty storage
        dict = {}
        for item in attribute_list:
            dict[item] = None
        self.att_dict = dict

# convenience functions
def getBookWithName(approxName, optional=None):
    approxAuthor = None

    if optional is not None:
        for key in optional:
            if key is 'authorName':
                approxAuthor = optional[key]

    book = objectInfo('book', {'approxName': approxName,
                               'approxAuthor': approxAuthor})
    return book

def getAuthorWithName(approxName, optional=None):
    author = objectInfo('author',{'approxName': approxName})
    return author

def scrapeAttributes(objectInfo, attributes):

    # get the list of info sources for this particular object type
    sourceInfo = object_types[objectInfo.type]
    if not isinstance(attributes, list):
        attributes = [attributes]

    found = {}
    for attribute in attributes:
        found[attribute] = False

    # fill them up
    for attribute in attributes:
        # if we haven't read this in yet
        if objectInfo.att_dict[attribute] is None:
            # make a call to get this attribute from somewhere
            sourceList = sourceInfo[attribute]
            for source in sourceList:
                sourceCall = source_call_dict[source]
                # do this call to fill up all the attributes that can be
                # filled up by this source
                sourceCall(objectInfo)
                # stop evaluating sources if this one returned the desired
                # info
                if objectInfo.att_dict[attribute] is not None:
                    found[attribute] = True
                    break

    # return the updated info
    return found, objectInfo
