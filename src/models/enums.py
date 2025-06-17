from enum import Enum

from dataclasses_json import config


class PartOfSpeech(Enum):
    NOUN = "noun"
    PRONOUN = "pronoun"
    INTRANSITIVEVERB = "intransitiveVerb"
    TRANSITIVEVERB = "transitiveVerb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    AUXILIARYVERB = "auxiliaryVerb"
    ARTICLE = "article"
    INTERJECTION = "interjection"
    CONJUNCTION = "conjunction"
    IDIOM = "idiom"

    # Add more parts of speech as needed


# Add serialization and deserialization config for PartOfSpeech
PartOfSpeechField = config(
    encoder=lambda x: x.value,  # Convert Enum to its value (e.g., 'noun')
    decoder=PartOfSpeech,  # Convert value back to Enum
)
