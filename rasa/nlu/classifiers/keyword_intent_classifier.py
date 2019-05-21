import os
import logging
import re
from typing import Any, Dict, Optional, Text

from rasa.nlu import utils
from rasa.nlu.components import Component
from rasa.nlu.training_data import Message

logger = logging.getLogger(__name__)


class KeywordIntentClassifier(Component):
    """Intent classifier using simple keyword matching.


    The classifier takes a list of keywords and associated intents as an input.
    A input sentence is checked for the keywords and the intent is returned.

    """

    provides = ["intent"]

    intent_keyword_map = {}

    def train(
        self,
        training_data: "TrainingData",
        cfg: Optional["RasaNLUModelConfig"] = None,
        **kwargs: Any
    ) -> None:
        self.intent_keyword_map.update(training_data.intent_keywords)

    def process(self, message: Message, **kwargs: Any) -> None:
        intent_name = self.parse(message.text)
        if intent_name is not None:
            intent = {"name": intent_name, "confidence": 1.0}
            message.set("intent", intent, add_to_output=True)

    def parse(self, text: Text) -> Optional[Text]:
        _text = text.lower()

        for intent, keywords in self.intent_keyword_map.items():
            for word in keywords:
                if re.search(r"\b" + word.lower() + r"\b", _text):
                    return intent

        return None

    def persist(self, file_name: Text, model_dir: Text) -> Dict[Text, Any]:
        """Persist this model into the passed directory.

        Return the metadata necessary to load the model again.
        """
        file_name = file_name + ".json"
        keyword_file = os.path.join(model_dir, file_name)
        utils.write_json_to_file(keyword_file, self.intent_keyword_map)

        return {"file": file_name}

    @classmethod
    def load(
        self,
        meta: Optional["Metadata"] = None,
        model_dir: Optional[Text] = None,
        model_metadata: "Metadata" = None,
        cached_component: Optional["KeywordIntentClassifier"] = None,
        **kwargs: Any
    ) -> "KeywordIntentClassifier":

        file_name = meta.get("file")
        if file_name is not None:
            keyword_file = os.path.join(model_dir, file_name)
            if os.path.exists(keyword_file):
                self.intent_keyword_map = utils.read_json_file(keyword_file)
            else:
                logger.warning(
                    "Failed to load IntentKeywordClassifier, maybe "
                    "{} does not exist.".format(keyword_file)
                )
        return self()
