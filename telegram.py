# basic telegram bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial/blob/master/part1/echobot.py

# python3: urllib.parse.quote_plus
# python2: urllib.pathname2url
import sys

import spacy

from intentExtraction.intents import entityWrapper
from utils.webHelpers import get_url, get_json_from_url
import urllib
import time
import config.apiKeys as apiKeys
import intentExtraction.intentExtractors as extractors
import intentExtraction.nlu_tools as nlu
import intentExtraction.intentHandlers as handlers
import logging
import neuralcoref
TOKEN = apiKeys.keys['telegram']['key']
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# the NLU interpreter of this bot
interpreter = nlu.get_default_interpreter(force_retrain=False)
# the intent extractor of this bot
intentExtractor = extractors.intentExtractor(interpreter)
handler_cache = {}

corefResolver = None
corefResolution = False
nlp = spacy.load('en')

if corefResolution:
    corefResolver = neuralcoref.Coref(nlp=nlp)


# the offset parameter tells Telegram from which update_id onwards to return updates
def get_updates(offset=None):
    # the call will return if there's no update for 100 seconds
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        # don't reply to stuff which has no message field (e.g. updates about edited messages)
        if "message" not in update:
            break

        # only reply to textual content
        if "text" not in update["message"]:
            break

        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]

        parsedIntent = intentExtractor.parse_sentence(text)

        for x in parsedIntent.ranking: print(x)

        print('Found ' + str(parsedIntent.type) + ' intent.')
        for entityWrapper in parsedIntent.entities:
            print(entityWrapper.type)



        # if cached, use previous
        if chat in handler_cache:
            intentHandler = handler_cache[chat]
        # generate new one for this chat
        else:
            intentHandler = handlers.intentHandler(chat,corefResolver=corefResolver,
                                                   nlp=nlp)
            # and store it
            handler_cache[chat] = intentHandler
        # get the appropriate response
        response = intentHandler.handleIntent(parsedIntent)

        print('Code = ' + str(response.state) + ";")

        # TODO think about how to deal with the other cases, e.g. follow-ups
        # if response.state = FOLLOWUP

        # reply to user
        send_message(response.responseString,chat)




def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    print('Ready.')
    # the last message we've seen
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
