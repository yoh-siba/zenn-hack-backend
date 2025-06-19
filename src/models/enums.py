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


def part_of_speech_to_japanese(part_of_speech: PartOfSpeech) -> str:
    """
    Convert PartOfSpeech enum to its Japanese equivalent.

    Args:
        part_of_speech (PartOfSpeech): The part of speech enum value.

    Returns:
        str: The Japanese equivalent of the part of speech.
    """
    translations = {
        PartOfSpeech.NOUN: "名詞",
        PartOfSpeech.PRONOUN: "代名詞",
        PartOfSpeech.INTRANSITIVEVERB: "自動詞",
        PartOfSpeech.TRANSITIVEVERB: "他動詞",
        PartOfSpeech.ADJECTIVE: "形容詞",
        PartOfSpeech.ADVERB: "副詞",
        PartOfSpeech.AUXILIARYVERB: "助動詞",
        PartOfSpeech.ARTICLE: "冠詞",
        PartOfSpeech.INTERJECTION: "感嘆詞",
        PartOfSpeech.CONJUNCTION: "接続詞",
        PartOfSpeech.IDIOM: "熟語",
    }
    return translations.get(part_of_speech, "不明")
