generic_response = {
    'greet': 'Hi! \nMy name is Talkative Bot and you can ask me questions ' +
             'about books and authors. \nTry asking for a summary, the ' +
             'price, the author or the ratings of a book or ask what books ' +
             'an author wrote.',
    'goodbye': 'Bye! Talk to you soon and don\'t forget to keep reading!'
}


# parse a Goodreads rating dict into a string
def format_ratings_dict(dict_in):
    # format with thousands separator
    n_ratings = dict_in['work_ratings_count']
    n_ratings = "{:,}".format(int(n_ratings))
    average_rating = dict_in['average_rating']
    return 'Average rating of ' + str(average_rating) + ' from ' + \
        n_ratings + ' ratings.'


# parse a dict of works author into a string
def format_works_dict(dict_in):
    works = dict_in.keys()
    toReturn = ''
    for work in works:
        toReturn = toReturn + work + '\n'
    return toReturn


def format_authors_dict(input):
    if isinstance(input, dict):
        authors = input.keys()
    else:
        authors = input
    toReturn = ''
    for author in authors:
        toReturn = toReturn + author + '\n'
    return toReturn


formatters = {
    'ratings': format_ratings_dict,
    'worksAuthored': format_works_dict,
    'authors': format_authors_dict
}


class replyGenerator(object):
    # for queries that require no more information
    def genericResponse(self, intentType):
        return generic_response[intentType]

    def generateResponse(self, objectInfo, requestedAttributes):
        toReturn = ''

        for attribute in requestedAttributes:
            # if there is a specific way to format this attribute, use that
            if attribute in formatters:
                toReturn = formatters[attribute](objectInfo.att_dict[attribute])
            # else, rely on generic fall-back
            else:
                toReturn = toReturn + str(attribute) + ":" + \
                        str(objectInfo.att_dict[attribute]) + "."

        return toReturn

    # TODO add more answers
    def info_not_found(self, attributeNotFound):
        return 'Could not find ' + str(attributeNotFound)

    # TODO add more answers
    def follow_up_no_entity_in_string(self, entityType):
        if entityType == 'bookName':
            return 'Could you specify the name of the book again?'
        if entityType == "authorName":
            return 'Could you specify the name of the author again?'

    # TODO add more answers
    def follow_up_no_object_found(self, entityType):
        if entityType == 'bookName':
            return 'No book of this name could be found! Could you specify again?'  # NOQA

        if entityType == 'authorName':
            return 'No author of this name could be found! Could you specify again?'  # NOQA
