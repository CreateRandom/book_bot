import spacy

import entityScraping.entityScrapers as scrapers
import intentExtraction.replyGenerators as generators

from entityScraping.entityScrapers import scrapeAttributes
from neuralcoref import Coref
# maps from an intent type to the requirements for satisfying this intent
requirements = {
    'greet': {},
    'goodbye': {},
    'summary': {'neededEntity': 'bookName', 'optionalEntities': ['authorName'], 'requestedAttributes': ['summary']},  # NOQA
    'price': {'neededEntity': 'bookName', 'optionalEntities': ['authorName'], 'requestedAttributes': ['price']},
    'authors': {'neededEntity': 'bookName', 'requestedAttributes': ['authors']},
    'ratings': {'neededEntity': 'bookName', 'optionalEntities': ['authorName'], 'requestedAttributes': ['ratings']},
    'reviews': {'neededEntity': 'bookName', 'optionalEntities': ['authorName'], 'requestedAttributes': ['reviews']},


    # list books for author
    'listBooksForAuthor': {'neededEntity': 'authorName', 'requestedAttributes': ['worksAuthored']},


}

# mappings from entities to object constructors
entity_object_mapping = {
    'bookName': scrapers.getBookWithName,
    'authorName': scrapers.getAuthorWithName
}

# map our entity set to SpaCy's pre-trained entities
custom_spacy_ner_mapping = {
    # ranked in descending order of desirability
    'bookName': ['WORK_OF_ART', 'ORG'],
    'authorName': 'PERSON'
}


class handlerResponse(object):
    OKAY = 0
    FOLLOW_UP_NO_ENTITY_IN_STRING = 1
    FOLLOW_UP_NO_OBJECT_FOUND = 2
    DESIRED_INFO_NOT_FOUND = 3

    def __init__(self, state, responseString):
        super().__init__()
        self.state = state
        self.responseString = responseString


# a class responsible for dealing with intents by obtaining the required
# information from a database / scraper
# should allow for follow-up questions if necessary
class intentHandler(object):
    def __init__(self, userId,
                 replyGenerator=generators.replyGenerator(),
                 corefResolver = None, nlp = None):
        super().__init__()
        self.userId = userId
        self.entityCache = {}
        self.convCache = []
        self.replyGenerator = replyGenerator
        self.corefResolver = corefResolver
        self.nlp = nlp

    def handleIntent(self, intentWrapper):
        req = requirements[intentWrapper.type]
        self.convCache.append(intentWrapper.message)

        # if there are no requirements, it's time for a generic response
        if len(req) == 0:
            return handlerResponse(handlerResponse.OKAY, self.replyGenerator.genericResponse(intentWrapper.type))  # NOQA

        neededEnt = req['neededEntity']

        optionalEnts = None
        if 'optionalEntities' in req:
            optionalEnts = req['optionalEntities']

        toRetrieve, optionalStorage = extract_entity_from_list(neededEnt,intentWrapper.entities,optionalEnts,lookForSpaCyEnts=True)

        # if we haven't found any entity to look for
        if toRetrieve is None:

            string = self.replyGenerator.follow_up_no_entity_in_string(neededEnt)  # NOQA


            # try resolving anaphora if possible
            if self.nlp is not None:
                text = intentWrapper.message

                anaphora_inducers = detectAnaphoraInducers(text,self.nlp)

                # if we find candidates for anaphora, handle that
                if len(anaphora_inducers) > 0:
                    if len(self.convCache) >= 2 and self.corefResolver is not None:
                        # use the last message
                        context = self.convCache[-2]
                        utterances = [context] + [intentWrapper.message]
                        clusters = self.corefResolver.one_shot_coref(utterances=utterances)
                        mentions = self.corefResolver.get_mentions()
                        most_rep = self.corefResolver.get_most_representative()
                        # TODO add more sophisticated handling once the functioning is improved
                        string = self.corefResolver.get_resolved_utterances()[0]
                    # tell user about co-reference
                    elif len(self.convCache) >= 2:
                        string = 'Detected co-reference, e.g. you referring back to a previously mentioned entity.' +\
                                 'Currently, the book cannot resolve which object you mean. Please rephrase query.'

                # fallback to indicate we didn't find entity in string
                return handlerResponse(handlerResponse.FOLLOW_UP_NO_ENTITY_IN_STRING, string)  # NOQA

        else:
            # TODO query the cache to find out whether we already have an object for this entity  # NOQA
            # and whether the object actually has the desired attributes stored
            if toRetrieve.value in self.entityCache:
                print("Cache call")

            # build the object anew
            else:
                objectConstructor = entity_object_mapping[toRetrieve.type]
                # construct the object with the value contained in the intent
                objectInfo = objectConstructor(toRetrieve.value, optional= optionalStorage)
                # scrape all desired attributes
                reqAttributes = req['requestedAttributes']
                # check if anything matching was found
                found, objectInfo = scrapeAttributes(objectInfo, reqAttributes)  # NOQA

                # TODO cache the object if it was found
                # if found: self.cache.add(objectInfo)

                # make sure we actually have the required info and apply processing steps
                for attribute in reqAttributes:
                    if not found[attribute]:
                        return handlerResponse(handlerResponse.DESIRED_INFO_NOT_FOUND, self.replyGenerator.info_not_found(attribute))  # NOQA

                # cache this object info
                # self.cache[toRetrieve.value] = objectInfo

                # reply here
                return handlerResponse(handlerResponse.OKAY, self.replyGenerator.generateResponse(objectInfo, reqAttributes))  # NOQA

# tag and return words that might cue anaphora, i.e. determiners or pronouns
def detectAnaphoraInducers(message,nlp):
    inducers = []
    text = nlp(message)
    for token in text:
        if(token.tag_ == 'DT' or token.tag_ == 'PRP'):
            inducers.append(token)

    return inducers


# finds the needed and optional entities in a list
def extract_entity_from_list(neededEnt,entList, optionalEnts = None, lookForSpaCyEnts=True):
    neededEntType = neededEnt

    # map to spacy ents if desired
    if lookForSpaCyEnts:
        # lump all possible entity names in a list
        temp = [neededEnt]
        spacy_ners = custom_spacy_ner_mapping[neededEnt]
        if not isinstance(spacy_ners, list):
            spacy_ners = [spacy_ners]
        temp = temp + spacy_ners
        neededEnt = temp

    # look for the required entity in the entities we found
    toRetrieve = None
    for entity in entList:
        if isinstance(neededEnt,str):
            if entity.type == neededEnt:
                toRetrieve = entity
                # set this to our standard type
                toRetrieve.type = neededEntType
                break
        elif isinstance(neededEnt,list):
            # ranked in descending order of desirability
            for string in neededEnt:
                if entity.type == string:
                    toRetrieve = entity
                    # set this to our standard type
                    toRetrieve.type = neededEntType
                    break

    # try to extract optional entities from the string
    optionalStorage = {}
    if optionalEnts is not None:

        for optional in optionalEnts:
            optionalType = optional

            if lookForSpaCyEnts:
                temp = [optional]
                spacy_ners = custom_spacy_ner_mapping[optional]
                if not isinstance(spacy_ners, list):
                    spacy_ners = [spacy_ners]
                temp = temp + spacy_ners
                optional = temp


            for entity in entList:
                if entity.type in optional:
                    optionalStorage[optionalType] = entity.value
                    break

    # toRetrieve: entities that have to be present; option
    return toRetrieve, optionalStorage

