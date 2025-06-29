import json
from datetime import datetime
from pathlib import Path

from src.models.types import PartOfSpeech, TranslationByGemini
from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.google_ai.unit.request_gemini import request_gemini_json


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def generate_translation(_content: str) -> list[MeaningSchema]:
    try:
        response, token_info = request_gemini_json(
            _contents=_content, _schema=list[TranslationByGemini]
        )
        if response is None:
            raise ValueError("Response is None")
        if not isinstance(response, list):
            raise ValueError("Response is not a list")
        if len(response) == 0:
            raise ValueError("Response list is empty")
        result = []
        for item in response:
            if not isinstance(item, TranslationByGemini):
                raise ValueError("Item is not of type TranslationByGemini")
            meaning = MeaningSchema(
                pos=PartOfSpeech(item.pos) if item.pos else None,
                translation=item.definition_jpn,
                pronunciation=item.pronunciation,
                example_eng=item.example_eng,
                example_jpn=item.example_jpn,
                rank=item.rank,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            result.append(meaning)
        result.sort(key=lambda x: x.rank)
        return result
    except Exception as e:
        print(f"翻訳生成エラー: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        raise ValueError("翻訳の生成に失敗しました") from e


if __name__ == "__main__":
    # Example usage
    content = """
英単語「run」の英語の各定義（以下のデータのdefinition）の値について、それぞれ対応する一言の簡潔な日本語訳を考えてください。
日本語に訳した際、同じ意味になる場合は、その重複は除いてください。
definition_engには、definitionの値をそのまま入れてください。
definition_jpnには、考えた日本語訳を入れてください。
posには、以下のデータのpartOfSpeechの値をそのまま入れてください。
pronunciationには、以下のデータのpronunciationの値をそのまま入れてください。
example_engには、examplesの最初の要素を、example_jpnにはその日本語訳を入れてください。
rankには、そのdefinitionの重要度を考慮して、rankを1から5の整数で設定してください。


### 例（「run」場合）
definitionが「move fast by using one's feet, with one foot off the ground at any given time」なら、意味は「走る」
「走る」はrunの意味として最も一般的な意味なので、rankは1に設定。

### データ
    {
      "definition": "a small stream",
      "partOfSpeech": "noun",
      "synonyms": [
        "rill",
        "rivulet",
        "runnel",
        "streamlet"
      ],
      "typeOf": [
        "stream",
        "watercourse"
      ]
    },
    {
      "definition": "have a particular form",
      "partOfSpeech": "verb",
      "synonyms": [
        "go"
      ],
      "typeOf": [
        "be"
      ],
      "examples": [
        "the story or argument runs as follows"
      ]
    },
    {
      "definition": "perform as expected when applied",
      "partOfSpeech": "verb",
      "synonyms": [
        "function",
        "go",
        "operate",
        "work"
      ],
      "hasTypes": [
        "service",
        "double",
        "cut",
        "roll",
        "serve"
      ],
      "verbGroup": [
        "work"
      ],
      "examples": [
        "Does this old car still run well?"
      ]
    },
    {
      "definition": "compete in a race",
      "partOfSpeech": "verb",
      "synonyms": [
        "race"
      ],
      "typeOf": [
        "contend",
        "vie",
        "compete"
      ],
      "hasTypes": [
        "horse-race",
        "show",
        "place",
        "campaign",
        "speed skate",
        "boat-race"
      ],
      "also": [
        "run off"
      ],
      "derivation": [
        "runner",
        "running"
      ],
      "examples": [
        "he is running the Marathon this year"
      ]
    },
    {
      "definition": "become undone",
      "partOfSpeech": "verb",
      "synonyms": [
        "unravel"
      ],
      "typeOf": [
        "disintegrate"
      ],
      "verbGroup": [
        "ladder"
      ]
    },
    {
      "definition": "a row of unravelled stitches",
      "partOfSpeech": "noun",
      "synonyms": [
        "ladder",
        "ravel"
      ],
      "typeOf": [
        "damage",
        "harm",
        "impairment"
      ],
      "examples": [
        "she got a run in her stocking"
      ]
    },
    {
      "definition": "a score in baseball made by a runner touching all four bases safely",
      "partOfSpeech": "noun",
      "synonyms": [
        "tally"
      ],
      "typeOf": [
        "score"
      ],
      "hasTypes": [
        "rbi",
        "unearned run",
        "earned run",
        "run batted in"
      ],
      "examples": [
        "the Yankees scored 3 runs in the bottom of the 9th"
      ]
    },
    {
      "definition": "run, stand, or compete for an office or a position",
      "partOfSpeech": "verb",
      "synonyms": [
        "campaign"
      ],
      "typeOf": [
        "race"
      ],
      "hasTypes": [
        "whistlestop",
        "register",
        "rerun",
        "cross-file",
        "stump"
      ],
      "examples": [
        "Who's running for treasurer this year?"
      ]
    },
    {
      "definition": "come unraveled or undone as if by snagging",
      "partOfSpeech": "verb",
      "synonyms": [
        "ladder"
      ],
      "typeOf": [
        "break",
        "come apart",
        "split up",
        "fall apart",
        "separate"
      ],
      "verbGroup": [
        "unravel"
      ],
      "examples": [
        "Her nylons were running"
      ]
    },
    {
      "definition": "direct or control; projects, businesses, etc.",
      "partOfSpeech": "verb",
      "synonyms": [
        "operate"
      ],
      "typeOf": [
        "direct"
      ],
      "hasTypes": [
        "work",
        "financier",
        "block",
        "warm up"
      ],
      "derivation": [
        "running"
      ],
      "examples": [
        "She is running a relief operation in the Sudan"
      ]
    },
    {
      "definition": "extend or continue for a certain period of time",
      "partOfSpeech": "verb",
      "synonyms": [
        "run for"
      ],
      "typeOf": [
        "last",
        "endure"
      ],
      "examples": [
        "The film runs 5 hours"
      ]
    },
    {
      "definition": "a race between candidates for elective office",
      "partOfSpeech": "noun",
      "synonyms": [
        "campaign",
        "political campaign"
      ],
      "typeOf": [
        "race"
      ],
      "hasTypes": [
        "senate campaign",
        "campaign for governor",
        "senate race",
        "governor's race"
      ],
      "examples": [
        "he is raising money for a Senate run"
      ]
    },
    {
      "definition": "include as the content; broadcast or publicize",
      "partOfSpeech": "verb",
      "synonyms": [
        "carry"
      ],
      "typeOf": [
        "disperse",
        "broadcast",
        "pass around",
        "spread",
        "disseminate",
        "propagate",
        "diffuse",
        "distribute",
        "circulate",
        "circularize",
        "circularise"
      ]
    },
    {
      "definition": "pass over, across, or through",
      "partOfSpeech": "verb",
      "synonyms": [
        "draw",
        "guide",
        "pass"
      ],
      "hasTypes": [
        "thread",
        "rub"
      ],
      "verbGroup": [
        "thread",
        "lead",
        "draw",
        "string"
      ]
    },
    {
      "definition": "the act of testing something",
      "partOfSpeech": "noun",
      "synonyms": [
        "test",
        "trial"
      ],
      "typeOf": [
        "attempt",
        "try",
        "endeavour",
        "endeavor",
        "effort"
      ],
      "hasTypes": [
        "preclinical trial",
        "field trial",
        "tryout",
        "trying on",
        "try-on",
        "fitting",
        "clinical trial",
        "clinical test",
        "audition",
        "snellen test",
        "ministry of transportation test",
        "mot",
        "mot test",
        "pilot program",
        "pilot project",
        "preclinical phase",
        "assay",
        "preclinical test",
        "double blind"
      ]
    },
    {
      "definition": "travel a route regularly",
      "partOfSpeech": "verb",
      "synonyms": [
        "ply"
      ],
      "typeOf": [
        "trip",
        "travel",
        "jaunt"
      ],
      "verbGroup": [
        "black market"
      ]
    },
    {
      "definition": "carry out a process or program, as on a computer or a machine",
      "partOfSpeech": "verb",
      "synonyms": [
        "execute"
      ],
      "typeOf": [
        "implement",
        "apply",
        "enforce"
      ],
      "hasTypes": [
        "step"
      ],
      "verbGroup": [
        "play"
      ],
      "examples": [
        "run a new program on the Mac"
      ]
    },
    {
      "definition": "flee; take to one's heels; cut and run",
      "partOfSpeech": "verb",
      "synonyms": [
        "break away",
        "bunk",
        "escape",
        "fly the coop",
        "head for the hills",
        "hightail it",
        "lam",
        "run away",
        "scarper",
        "scat",
        "take to the woods",
        "turn tail"
      ],
      "typeOf": [
        "go forth",
        "leave",
        "go away"
      ],
      "hasTypes": [
        "skedaddle",
        "take flight",
        "fly",
        "flee"
      ],
      "examples": [
        "If you see this man, run!"
      ]
    },
    {
      "definition": "cause something to pass or lead somewhere",
      "partOfSpeech": "verb",
      "synonyms": [
        "lead"
      ],
      "typeOf": [
        "make pass",
        "pass"
      ],
      "verbGroup": [
        "pass",
        "range",
        "draw",
        "guide"
      ]
    },
    {
      "definition": "have a tendency or disposition to do or be something; be inclined",
      "partOfSpeech": "verb",
      "synonyms": [
        "be given",
        "incline",
        "lean",
        "tend"
      ],
      "typeOf": [
        "be"
      ],
      "hasTypes": [
        "suffer",
        "gravitate",
        "take kindly to"
      ],
      "examples": [
        "These dresses run small"
      ]
    },
    {
      "definition": "stretch out over a distance, space, time, or scope; run or extend between two points or beyond a certain point",
      "partOfSpeech": "verb",
      "synonyms": [
        "extend",
        "go",
        "lead",
        "pass"
      ],
      "typeOf": [
        "be"
      ],
      "hasTypes": [
        "ray",
        "go deep",
        "underrun",
        "radiate",
        "come",
        "go far"
      ],
      "verbGroup": [
        "range"
      ],
      "also": [
        "run along"
      ],
      "examples": [
        "Service runs all the way to Cranbury"
      ]
    },
    {
      "definition": "the act of running; traveling on foot at a fast pace",
      "partOfSpeech": "noun",
      "synonyms": [
        "running"
      ],
      "typeOf": [
        "travel",
        "locomotion"
      ],
      "hasTypes": [
        "sprint",
        "dash"
      ],
      "examples": [
        "he broke into a run",
        "his daily run keeps him fit"
      ]
    },
    {
      "definition": "cause to emit recorded audio or video",
      "partOfSpeech": "verb",
      "synonyms": [
        "play"
      ],
      "verbGroup": [
        "play",
        "execute"
      ]
    },
    {
      "definition": "keep company",
      "partOfSpeech": "verb",
      "synonyms": [
        "consort"
      ],
      "typeOf": [
        "accompany"
      ],
      "examples": [
        "the heifers run with the bulls to produce offspring"
      ]
    },
    {
      "definition": "change or be different within limits",
      "partOfSpeech": "verb",
      "synonyms": [
        "range"
      ],
      "typeOf": [
        "be"
      ],
      "verbGroup": [
        "pass",
        "lead",
        "go",
        "extend"
      ],
      "examples": [
        "Interest rates run from 5 to 10 percent"
      ]
    },
    {
      "definition": "deal in illegally, such as arms or liquor",
      "partOfSpeech": "verb",
      "synonyms": [
        "black market"
      ],
      "inCategory": [
        "crime",
        "criminal offence",
        "criminal offense",
        "law-breaking"
      ],
      "typeOf": [
        "merchandise",
        "trade"
      ],
      "verbGroup": [
        "ply"
      ]
    },
    {
      "definition": "continue to exist",
      "partOfSpeech": "verb",
      "synonyms": [
        "die hard",
        "endure",
        "persist",
        "prevail"
      ],
      "typeOf": [
        "continue"
      ],
      "hasTypes": [
        "reverberate",
        "carry over"
      ]
    },
    {
      "definition": "a race run on foot",
      "partOfSpeech": "noun",
      "synonyms": [
        "foot race",
        "footrace"
      ],
      "typeOf": [
        "race"
      ],
      "hasTypes": [
        "track event",
        "steeplechase",
        "marathon",
        "obstacle race",
        "fun run",
        "funrun"
      ],
      "examples": [
        "she broke the record for the half-mile run"
      ]
    },
    {
      "definition": "an unbroken series of events",
      "partOfSpeech": "noun",
      "synonyms": [
        "streak"
      ],
      "typeOf": [
        "succession"
      ],
      "hasTypes": [
        "losing streak",
        "winning streak"
      ],
      "examples": [
        "Nicklaus had a run of birdies"
      ]
    },
    {
      "definition": "reduce or cause to be reduced from a solid to a liquid state, usually by heating",
      "partOfSpeech": "verb",
      "synonyms": [
        "melt",
        "melt down"
      ],
      "typeOf": [
        "resolve",
        "break up",
        "dissolve"
      ],
      "hasTypes": [
        "fuse",
        "render",
        "try"
      ],
      "verbGroup": [
        "bleed"
      ]
    },
    {
      "definition": "the pouring forth of a fluid",
      "partOfSpeech": "noun",
      "synonyms": [
        "discharge",
        "outpouring"
      ],
      "typeOf": [
        "flow",
        "flowing"
      ],
      "hasTypes": [
        "leak",
        "jet",
        "spirt",
        "outflow",
        "escape",
        "leakage",
        "squirt",
        "spurt"
      ],
      "derivation": [
        "runny"
      ]
    },
    {
      "definition": "(American football) a play in which a player attempts to carry the ball through or past the opposing team",
      "partOfSpeech": "noun",
      "synonyms": [
        "running",
        "running game",
        "running play"
      ],
      "inCategory": [
        "american football game",
        "american football"
      ],
      "typeOf": [
        "football play"
      ],
      "hasTypes": [
        "rush",
        "draw play",
        "return",
        "reverse",
        "rushing",
        "sweep",
        "draw",
        "end run"
      ],
      "examples": [
        "the defensive line braced to stop the run",
        "the coach put great emphasis on running"
      ]
    },
    {
      "definition": "be diffused",
      "partOfSpeech": "verb",
      "synonyms": [
        "bleed"
      ],
      "typeOf": [
        "spread out",
        "spread",
        "fan out",
        "diffuse"
      ],
      "hasTypes": [
        "crock"
      ],
      "verbGroup": [
        "melt down",
        "melt"
      ],
      "examples": [
        "These dyes and colors are guaranteed not to run"
      ]
    },
    {
      "definition": "move along, of liquids",
      "partOfSpeech": "verb",
      "synonyms": [
        "course",
        "feed",
        "flow"
      ],
      "typeOf": [
        "move"
      ],
      "hasTypes": [
        "run down",
        "drain",
        "dribble",
        "eddy",
        "whirlpool",
        "whirl",
        "well out",
        "filter",
        "flush",
        "waste",
        "trickle",
        "circulate",
        "tide",
        "swirl",
        "gush",
        "gutter",
        "surge",
        "stream",
        "jet",
        "spill",
        "seep",
        "ooze",
        "run out",
        "run off",
        "purl",
        "pour"
      ],
      "also": [
        "run over"
      ]
    },
    {
      "definition": "progress by being changed",
      "partOfSpeech": "verb",
      "synonyms": [
        "go",
        "move"
      ],
      "typeOf": [
        "change"
      ],
      "examples": [
        "run through your presentation before the meeting"
      ]
    },
    {
      "definition": "pursue for food or sport (as of wild animals)",
      "partOfSpeech": "verb",
      "synonyms": [
        "hunt",
        "hunt down",
        "track down"
      ],
      "typeOf": [
        "catch",
        "capture"
      ],
      "hasTypes": [
        "jack",
        "ambush",
        "drive",
        "rabbit",
        "seal",
        "falcon",
        "course",
        "whale",
        "ferret",
        "forage",
        "fowl",
        "foxhunt",
        "snipe",
        "still-hunt",
        "jacklight",
        "scrounge",
        "hawk",
        "poach",
        "turtle"
      ],
      "verbGroup": [
        "hunt"
      ],
      "examples": [
        "The dogs are running deer"
      ]
    },
    {
      "definition": "an unbroken chronological sequence",
      "partOfSpeech": "noun",
      "typeOf": [
        "chronological sequence",
        "successiveness",
        "sequence",
        "succession",
        "chronological succession"
      ],
      "examples": [
        "the play had a long run on Broadway",
        "the team enjoyed a brief run of victories"
      ]
    },
    {
      "definition": "a regular trip",
      "partOfSpeech": "noun",
      "typeOf": [
        "trip"
      ],
      "examples": [
        "the ship made its run in record time"
      ]
    },
    {
      "definition": "a short trip",
      "partOfSpeech": "noun",
      "typeOf": [
        "trip"
      ],
      "examples": [
        "take a run into town"
      ]
    },
    {
      "definition": "be affected by; be subjected to",
      "partOfSpeech": "verb",
      "typeOf": [
        "incur"
      ],
      "examples": [
        "run a temperature",
        "run a risk"
      ]
    },
    {
      "definition": "be operating, running or functioning",
      "partOfSpeech": "verb",
      "typeOf": [
        "operate",
        "work",
        "function",
        "go"
      ],
      "verbGroup": [
        "operate",
        "work",
        "function",
        "go"
      ],
      "antonyms": [
        "idle"
      ],
      "derivation": [
        "running"
      ],
      "examples": [
        "The car is still running--turn it off!"
      ]
    },
    {
      "definition": "carry out",
      "partOfSpeech": "verb",
      "typeOf": [
        "carry out",
        "carry through",
        "fulfill",
        "accomplish",
        "fulfil",
        "execute",
        "action"
      ],
      "examples": [
        "run an errand"
      ]
    },
    {
      "definition": "cause an animal to move fast",
      "partOfSpeech": "verb",
      "typeOf": [
        "move",
        "displace"
      ],
      "verbGroup": [
        "hunt",
        "hunt down",
        "track down"
      ],
      "examples": [
        "run the dogs"
      ]
    },
    {
      "definition": "cause to perform",
      "partOfSpeech": "verb",
      "typeOf": [
        "process",
        "treat"
      ],
      "hasTypes": [
        "rerun"
      ],
      "verbGroup": [
        "play"
      ],
      "examples": [
        "run a subject",
        "run a process"
      ]
    },
    {
      "definition": "change from one state to another",
      "partOfSpeech": "verb",
      "typeOf": [
        "go",
        "become",
        "get"
      ],
      "examples": [
        "run amok",
        "run rogue",
        "run riot"
      ]
    },
    {
      "definition": "cover by running; run a certain distance",
      "partOfSpeech": "verb",
      "typeOf": [
        "pass"
      ]
    },
    {
      "definition": "make without a miss",
      "partOfSpeech": "verb",
      "inCategory": [
        "sport",
        "athletics"
      ],
      "typeOf": [
        "win",
        "succeed",
        "bring home the bacon",
        "deliver the goods",
        "come through"
      ]
    },
    {
      "definition": "move about freely and without restraint, or act as if running around in an uncontrolled way",
      "partOfSpeech": "verb",
      "typeOf": [
        "go",
        "locomote",
        "travel",
        "move"
      ],
      "examples": [
        "who are these people running around in the building?",
        "She runs around telling everyone of her troubles",
        "let the dogs run free"
      ]
    },
    {
      "definition": "move fast by using one's feet, with one foot off the ground at any given time",
      "partOfSpeech": "verb",
      "typeOf": [
        "travel rapidly",
        "hurry",
        "speed",
        "zip"
      ],
      "hasTypes": [
        "lope",
        "clip",
        "romp",
        "scuttle",
        "trot",
        "scurry",
        "scamper",
        "jog",
        "skitter",
        "hare",
        "rush",
        "outrun",
        "run bases",
        "sprint",
        "streak"
      ],
      "also": [
        "run away",
        "run around"
      ],
      "derivation": [
        "runner",
        "running"
      ],
      "examples": [
        "Don't run--you'll be out of breath"
      ]
    },
    {
      "definition": "occur persistently",
      "partOfSpeech": "verb",
      "typeOf": [
        "occur"
      ],
      "verbGroup": [
        "die hard",
        "prevail",
        "persist",
        "endure"
      ],
      "examples": [
        "Musical talent runs in the family"
      ]
    },
    {
      "definition": "run with the ball; in such sports as football",
      "partOfSpeech": "verb",
      "inCategory": [
        "athletics",
        "sport"
      ],
      "derivation": [
        "running"
      ]
    },
    {
      "definition": "sail before the wind",
      "partOfSpeech": "verb",
      "typeOf": [
        "sail"
      ]
    },
    {
      "definition": "set animals loose to graze",
      "partOfSpeech": "verb",
      "typeOf": [
        "release",
        "free",
        "unloose",
        "unloosen",
        "loose",
        "liberate"
      ]
    },
    {
      "definition": "the continuous period of time during which something (a machine or a factory) operates or continues in operation",
      "partOfSpeech": "noun",
      "typeOf": [
        "period",
        "time period",
        "period of time"
      ],
      "hasTypes": [
        "press run",
        "print run",
        "run-time"
      ],
      "examples": [
        "the assembly line was on a 12-hour run"
      ]
    },
    {
      "definition": "the production achieved during a continuous period of operation (of a machine or factory etc.)",
      "partOfSpeech": "noun",
      "typeOf": [
        "indefinite quantity"
      ],
      "examples": [
        "a daily run of 100,000 gallons of paint"
      ]
    },
    {
      "definition": "travel rapidly, by any (unspecified) means",
      "partOfSpeech": "verb",
      "typeOf": [
        "go",
        "move",
        "locomote",
        "travel"
      ],
      "examples": [
        "She always runs to Italy, because she has a lover there"
      ]
    },
    {
      "definition": "unrestricted freedom to use",
      "partOfSpeech": "noun",
      "typeOf": [
        "liberty"
      ],
      "examples": [
        "he has the run of the house"
      ]
    }

    ### 発音データ
      "pronunciation": {
    "all": "rən"
  }
"""
    result = generate_translation(content)
    result.sort(key=lambda x: x.rank)

    if result is None:
        print("No translation generated.")
    # 出力ディレクトリの作成
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    # 現在時刻をファイル名に使用
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{current_time}_word.json"
    # 結果をJSONファイルに出力
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            [meaning.to_dict() for meaning in result],
            f,
            ensure_ascii=False,
            indent=2,
            default=datetime_handler,
        )
    print(f"Translation saved to: {output_file}")
