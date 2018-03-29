from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer, Interpreter

import intentExtraction.intentExtractors as intentExtractors
import intentExtraction.intents as intents
import entityScraping.entityScrapers as entityScrapers
from entityScraping.entityScrapers import scrapeAttributes


def get_default_interpreter(force_retrain=False):
    config = 'config/rasa_config.json'

    path = retrieve_model_path()
    # if there is no previously used model or we want to enforce a retrain
    if path is None or force_retrain:
        # retrain the model
        model = train_rasa_model(config, 'intentExtraction/rasa_training_data.json')
    else:
        model = path
    return build_interpreter(config, model)


def train_rasa_model(config_path, data_path):
    training_data = load_data(data_path)

    config = RasaNLUConfig(config_path)

    trainer = Trainer(config)

    trainer.train(training_data)
    # persist the model
    storage_path = trainer.persist('book_bot_models')

    store_model_path(storage_path)

    return storage_path


def build_interpreter(config_path, model):
    config = RasaNLUConfig(config_path)

    return Interpreter.load(model, config)


model_path = "modelpath"


def retrieve_model_path():
    try:
        file = open(model_path, "r")
        path = file.read()
        file.close()
        return path
    except:
        return None


def store_model_path(storage_path):
    file = open(model_path, "w")

    file.write(storage_path)

    file.close()
