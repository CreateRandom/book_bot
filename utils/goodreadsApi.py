import requests
from xml.etree import ElementTree
import config.apiKeys as apiKeys

base_url = apiKeys.keys['goodreads']['base_url']
key = apiKeys.keys['goodreads']['key']
secret = apiKeys.keys['goodreads']['secret']


''' TODO
See a series
See all series by an author
See all series a work is in
Get reviews somehow.. so far only got widget codes to implement...
'''


def do_json_request(url):
    response = requests.get(url)
    # TODO think about how to fix this in more durable fashion
    if response.status_code is not 200:
        return None
      #  raise ValueError('Non-200 status code returned: {0} on url {1}'.format(response.status_code, url))  # NOQA
    return response.json()


def do_xml_request(url):
    response = requests.get(url)
    if response.status_code is not 200:
        raise ValueError('Non-200 status code returned: {0} on url {1}'.format(response.status_code, url))  # NOQA
    return ElementTree.fromstring(response.content)


# Input: goodreadsid, output: Goodreads Work Id
def get_workid_id(goodreadsid):
    url = base_url + "book/id_to_work_id/" + goodreadsid + \
          "?key=" + key
    xml_response = do_xml_request(url)
    work_ids = xml_response.find('work-ids')
    work_id = work_ids[0].text
    return work_id

# ###################### ISBN input #########################


# Input: isbn string, output: Goodreads Book Id
def get_goodreadsid_isbn(isbn):
    url = base_url + "book/isbn_to_id/" + isbn + \
          "?format=xml" + \
          "&key=" + key
    ID = do_json_request(url)
    return ID


# Input: isbn string, output: dictionary with rating values
def get_review_stats(isbn):
    url = base_url + "book/review_counts.json?isbns=" + isbn + \
          "&key=" + key
    json_response = do_json_request(url)
    if json_response is not None:
        ratings = json_response['books'][0]
        return ratings
    return None

# Input: isbn string, output: dict of info for book
# TODO figure out how booklinks work...
def get_basic_info(isbn):
    info = {}
    url = base_url + "book/isbn/" + isbn + "?key=" + key
    xml_response = do_xml_request(url)

    book = xml_response.find('book')
    info['goodreadsid'] = book.find('id').text
    info['title'] = book.find('title').text
    info['isbn'] = book.find('isbn').text
    info['isbn13'] = book.find('isbn13').text
    info['image_url'] = book.find('image_url').text
    info['publication_year'] = book.find('publication_year').text
    info['publication_month'] = book.find('publication_month').text
    info['publication_day'] = book.find('publication_day').text
    info['publisher'] = book.find('publisher').text
    info['language_code'] = book.find('language_code').text
    info['is_ebook'] = book.find('is_ebook').text
    info['num_pages'] = book.find('num_pages').text
    info['format'] = book.find('format').text
    info['edition_information'] = book.find('edition_information').text
    info['ratings_count'] = book.find('ratings_count').text
    info['text_reviews_count'] = book.find('text_reviews_count').text
    info['url'] = book.find('url').text
    info['link'] = book.find('link').text

    bookwork = book.find('work')
    info['work'] = {}
    info['work']['id'] = bookwork.find('id').text
    info['work']['books_count'] = bookwork.find('books_count').text
    info['work']['best_book_id'] = bookwork.find('best_book_id').text
    info['work']['reviews_count'] = bookwork.find('reviews_count').text
    info['work']['ratings_count'] = bookwork.find('ratings_count').text
    info['work']['text_reviews_count'] = bookwork.find('text_reviews_count').text
    info['work']['original_publication_year'] = bookwork.find('original_publication_year').text
    info['work']['original_publication_month'] = bookwork.find('original_publication_month').text
    info['work']['original_publication_day'] = bookwork.find('original_publication_day').text
    info['work']['original_title'] = bookwork.find('original_title').text
    info['work']['rating_dist'] = bookwork.find('rating_dist').text

    authors = book.find('authors')
    info['authors'] = {}
    for author in authors:
        name = author.find('name').text
        info['authors'][name] = {}
        info['authors'][name]['id'] = author.find('id').text
        info['authors'][name]['link'] = author.find('link').text
        info['authors'][name]['average_rating'] = author.find('average_rating').text
        info['authors'][name]['ratings_count'] = author.find('ratings_count').text
        info['authors'][name]['text_reviews_count'] = author.find('text_reviews_count').text

    buy_links = book.find('buy_links')
    info['buy_links'] = {}
    for buy_link in buy_links:
        name = buy_link.find('name').text
        info['buy_links'][name] = buy_link.find('link').text

    series_works = book.find('series_works')
    info['series_works'] = {}
    for series_work in series_works:
            series = series_work.find('series')
            title = series.find('title').text
            info['series_works'][title] = {}
            info['series_works'][title]['series_id'] = series_work.find('id').text
            info['series_works'][title]['id'] = series.find('id').text
            info['series_works'][title]['description'] = series.find('description').text
            info['series_works'][title]['note'] = series.find('note').text
            info['series_works'][title]['series_works_count'] = series.find('series_works_count').text
            info['series_works'][title]['primary_work_count'] = series.find('primary_work_count').text
            info['series_works'][title]['numbered'] = series.find('numbered').text

    similar_books = book.find('similar_books')
    info['similar_books'] = {}
    for similar_book in similar_books:
        title = similar_book.find('title').text
        info['similar_books'][title] = {}
        info['similar_books'][title]['id'] = similar_book.find('id').text
        info['similar_books'][title]['title_without_series'] = similar_book.find('title_without_series').text
        info['similar_books'][title]['link'] = similar_book.find('link').text
        info['similar_books'][title]['image_url'] = similar_book.find('image_url').text
        info['similar_books'][title]['num_pages'] = similar_book.find('num_pages').text
        info['similar_books'][title]['isbn'] = similar_book.find('isbn').text
        info['similar_books'][title]['isbn13'] = similar_book.find('isbn13').text
        info['similar_books'][title]['average_rating'] = similar_book.find('average_rating').text
        info['similar_books'][title]['ratings_count'] = similar_book.find('ratings_count').text
        info['similar_books'][title]['publication_year'] = similar_book.find('publication_year').text
        info['similar_books'][title]['publication_month'] = similar_book.find('publication_month').text
        info['similar_books'][title]['publication_day'] = similar_book.find('publication_day').text
        similar_book_work = similar_book.find('work')
        info['similar_books'][title]['work_id'] = similar_book_work.find('id').text
        similar_book_authors = similar_book.find('authors')
        info['similar_books'][title]['authors'] = {}
        for author in similar_book_authors:
            name = author.find('name').text
            info['similar_books'][title]['authors'][name] = {}
            info['similar_books'][title]['authors'][name]['id'] = author.find('id').text
            info['similar_books'][title]['authors']['link'] = author.find('link').text

        return info


# Main info call for book - Input: isbn string, output: dict of info for book
def get_book_info(isbn):
    book_info = get_basic_info(isbn)
    add_info = get_review_stats(isbn)
    book_info['reviews_count'] = add_info['reviews_count']
    book_info['average_rating'] = add_info['average_rating']
    return book_info


# ####### Author #############


# Input: author name, output: author_id
def get_author_id(author_name):
    url = base_url + "api/author_url/" + author_name + \
          "?key=" + key
    xml_response = do_xml_request(url)
    author = xml_response.find('author')
    author_id = author.get('id')
    return author_id


# Input: author_id goodreads, output: author dict with author's books
def get_authors_books(author_id, page=1):
    info = {}
    url = base_url + "author/list/" + str(author_id) + \
          "?format=xml" + \
          "&key=" + key + \
          "&page=" + str(page)
    xml_response = do_xml_request(url)

    author = xml_response.find('author')
    books = author.find('books')
    for book in books:
        title = book.find('title').text
        info[title] = {}
        info[title]['id'] = book.find('id').text
        info[title]['isbn'] = book.find('isbn').text
        info[title]['link'] = book.find('link').text
        # If want more info on specific book, call get_book_info using isbn

    # Deal with pagination
    if 'end' in books.keys():
        if books.get('end') < books.get('total'):
            newpage = page + 1
            next_page_info = get_authors_books(author_id, page=newpage)
            info.update(next_page_info)

    return info


# Input: author_id, output: dict with author info, no books
def get_author_show(author_id):
    info = {}
    url = base_url + "author/show/" + str(author_id) + \
        "?format=xml" + \
        "&key=" + key
    xml_response = do_xml_request(url)

    author = xml_response.find('author')
    info['id'] = author.find('id').text
    info['name'] = author.find('name').text
    info['link'] = author.find('link').text
    info['fans_count'] = author.find('fans_count').text
    info['author_followers_count'] = author.find('author_followers_count').text
    info['image_url'] = author.find('image_url').text
    info['about'] = author.find('about').text
    info['influences'] = author.find('influences').text
    info['works_count'] = author.find('works_count').text
    info['gender'] = author.find('gender').text
    info['hometown'] = author.find('hometown').text
    info['born_at'] = author.find('born_at').text
    info['died_at'] = author.find('died_at').text
    info['goodreads_author'] = author.find('goodreads_author').text
    if info['goodreads_author']:
        user = author.find('user')
        info['user_id'] = user.find('id').text

    return info


# Main author function - input: author_name, output dict of author info
def get_author_info(author_name):
    author_id = get_author_id(author_name)
    author_info = get_author_show(author_id)
    author_books_info = get_authors_books(author_id)
    author_info['books'] = author_books_info
    return author_info


# Main author funciton with id - Input: author_id, output dict of author info
def get_author_info_id(author_id):
    author_info = get_author_show(author_id)
    author_books_info = get_authors_books(author_id)
    author_info['books'] = author_books_info
    return author_info



# TODO figure out if / how to extract those
def get_reviews(isbn):
    return None