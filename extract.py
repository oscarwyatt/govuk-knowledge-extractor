from bs4 import BeautifulSoup, NavigableString
import spacy
import os.path, sys
import textacy

sys.path.append(os.path.join(os.getcwd(), "../govuk-knowledge-graph"))
from src.eligibility.govNER.govNER import GovNER


patterns = [
    {
        "pattern": " is a party to the ",
        "join": "PARTY_TO",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": False,
        "object_types": [],
        "object_regex": "POS:NOUN:+ POS:ADP:? POS:PROPN:+ POS:ADP:* POS:PROPN:*",
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
    {
        "pattern": " is a party to ",
        "join": "PARTY_TO",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": False,
        "object_types": [],
        "object_regex": "POS:NOUN:+ POS:ADP:? POS:PROPN:+ POS:ADP:* POS:PROPN:*",
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
    {
        "pattern": " is a member of the ",
        "join": "MEMBER",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": True,
        "object_types": ["ORGANIZATION", "LOCATION"],
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
    {
        "pattern": " is a member of ",
        "join": "MEMBER",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": True,
        "object_types": ["ORGANIZATION", "LOCATION"],
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
    {
        "pattern": " is a branch of ",
        "join": "BRANCH",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": True,
        "object_types": ["ORGANIZATION", "LOCATION"],
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
    {
        "pattern": " is a ",
        "join": "INSTANCE_OF",
        "subject_types": ["ORGANIZATION", "LOCATION"],
        "any_subject_types": True,
        "object_types": ["ORGANIZATION", "LOCATION"],
        "any_object_types": True,
        "has_direction": True,
        "direction_is_subject_to_object": False,
    },
]

if not os.path.isfile('files_matching_pattern.txt'):
    pattern_command = "|".join([pattern["pattern"] for pattern in patterns])
    command = f"./find_content -p '{pattern_command}'"
    os.system(command)

filenames = open(str("files_matching_pattern.txt")).read().split("\n")


test_sentences = [
    {
        'sentence': 'Access to Work (AtW) is a specialist disability programme delivered by Jobcentre Plus (JCP), which provides practical advice and support to disabled people and their employers to help them overcome work related obstacles resulting from disability',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "Access to Work",
                'expected_object': "specialist disability programme",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "specialist disability programme",
                'expected_object': "disability programme",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "disability programme",
                'expected_object': "programme",
            },
        ]


    },
    {
        'sentence': 'Council tax is a tax on domestic property set by local authorities in order to collect sufficient revenue to meet their demand',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "Council tax",
                'expected_object': "tax",
            }
        ]
    },
    {
        'sentence': 'London Councils is a membership organisation for the 32 London boroughs and the City of London',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "London Councils",
                'expected_object': "membership organisation",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "membership organisation",
                'expected_object': "organisation",
            },
        ]
    },
    {
        'sentence': 'Sport England is a public body and invests more than £300 million National Lottery and government money each year in projects and programmes that help people get active and play sport',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "Sport England",
                'expected_object': "public body",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "public body",
                'expected_object': "body",
            }
        ]

    },
    {
        'sentence': 'UKTI is a UK government department which works with businesses based in the United Kingdom to help them achieve their potential overseas',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "UKTI",
                'expected_object': "UK government department",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "UK government department",
                'expected_object': "government department",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "government department",
                'expected_object': "department",
            },
        ]
    },
    {
        'sentence': 'Peter is a UK National',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "Peter",
                'expected_object': "UK National",
                'would_be_nice': 'resolve to Peter Fernandes Cardy'
            }
        ]
    },
    {
        'sentence': 'Burma is a party to the Convention on International Trade in Endangered Species (CITES)',
        'expected_facts': [
            {
                'expected_relationship': "PARTY_TO",
                'expected_subject': "Burma",
                'expected_object': "Convention on International Trade in Endangered Species",
            }
        ]
    },
    {
        'sentence': 'British Independent Retailers Association (BIRA)  is a membership association dedicated to retail businesses',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "British Independent Retailers Association",
                'expected_object': "membership association",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "membership association",
                'expected_object': "association",
            }
        ]
    },
    {
        'sentence': 'Social Work England is a specialist body taking a new approach to regulating social workers in their vital roles',
        'expected_facts': [
            {
                'expected_relationship': "INSTANCE_OF",
                'expected_subject': "Social Work England",
                'expected_object': "specialist body",
            },
            {
                'expected_relationship': "SUBCLASS",
                'expected_subject': "specialist body",
                'expected_object': "body",
            }
        ]
    },
]

successes = []
failures = []
for test in test_sentences:
    facts = process_sentence(nlp, ner, chunker, test['sentence'], patterns)
    success = True
    for expected_fact in test['expected_facts']:
        found = False
        for fact in facts:
            if fact.subject == expected_fact['expected_subject'] and fact.object == expected_fact['expected_object'] and fact.relationship == expected_fact['expected_relationship']:
                found = True
        if not found:
            success = False
    if success:
        successes.append(test)
    else:
        failures.append(test)

len(successes)
len(failures)



to_expand_into = [
    {
        'sentence': 'China is a world leader in the market for raw materials for the pharmaceutical industry and closer collaboration with MHRA will support the promotion of innovation, good practice, and protect UK patients',
        'expected_relationship': "INSTANCE_OF",
        'expected_subject': "China",
        'expected_object': "world leader",
        'expected_extra_entities': "in the market for raw materials for the pharmaceutical industry",
    },
    {
        'sentence': 'UK is a world leader in the sales of TV content, with Downtown Abbey watched in 250 territories worldwide',
        'expected_relationship': "INSTANCE_OF",
        'expected_subject': "UK",
        'expected_object': "world leader",
        'expected_extra_entities': "in the sales of TV content",
    },
    {
        'sentence': 'CCS is a prime opportunity for UK manufacturing and I am delighted to see Scottish based companies like Howden and Doosan Power Systems, as well as MAST Carbon based in Basingstoke, seizing the opportunity to create jobs for skilled workers and growth for the economy',
        'expected_relationship': "INSTANCE_OF",
        'expected_subject': "CCS",
        'expected_object': "opportunity",
        'expected_extra_entities': "for UK manufacturing",
    }

]


ner = GovNER()
nlp = spacy.load("en_ud_model_lg")
chunker = EntityChunker(nlp)

knowledge = []
for i, filename in enumerate(filenames):
    f = open(str(filename)).read()
    texts = extract_texts(f)
    entities_for_file = []
    print(f"index: {i}")
    for text in texts:
        entities_for_file += process_text(nlp, ner, chunker, text, patterns)
    for entity in entities_for_file:
        entry = {'base_path': str(filename)}
        entry.update(entity)
        knowledge.append(entry)



def extract_texts(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in ['b', 'i', 'u', 'a', 'abbr']:
        for match in soup.findAll(tag):
            match.replaceWithChildren()
            # If we don't extract them, the old tags stick
            # around and mess up the soup.strings call
            # match.extract()
    [x.extract() for x in soup.findAll('script')]
    soup = BeautifulSoup(str(soup), 'html.parser')
    return list(soup.strings)

def has_pattern(text, patterns):
    for pattern in patterns:
        if pattern['pattern'] in text:
            return True

def process_text(nlp, ner, chunker, text, patterns):
    entities = []
    if has_pattern(text, patterns):
        for sentence in text.split("."):
            entities += process_sentence(nlp, ner, chunker, sentence, patterns)
    return entities

def process_sentence(nlp, ner, chunker, sentence, patterns):
    if has_pattern(sentence, patterns):
        return extract_knowledge(nlp, ner, chunker, sentence, patterns)
    return []


# Because there are many patterns, some of which are sub patterns of others, we want to search for them in a greedy manner
# example: text = "Germany is a member of NATO"
# " is a " is a pattern, as is " is a member of "
# but we don't want to get the twin facts "Germany is member" and "Germany is a member of"
# we only want "Germany is a member of" because it's more specific/useful
# thus the patterns should be arranged in most specific->most general
# and we return early when we've found the most specific pattern
def extract_knowledge(nlp, ner, chunker, sentence, patterns):
    for pattern in patterns:
        knowledge = extract_facts_for_pattern(nlp, ner, chunker, sentence, pattern)
        if any(knowledge):
            return knowledge
    return []

def extract_facts_for_pattern(nlp, ner, chunker, sentence, pattern):
    # Split sentence by the pattern, so that "Germany is a country" becomes ["Germany", "country"]
    words = sentence.split(pattern['pattern'])
    # Sometimes a sentence will have more or less entries after the split
    # eg "Is a dog indeed a man's best friend? Let's find out" wouldn't work
    # eg "Germany is a country, Paul is a German" which ought to be possible but is harder to implement
    # might be good to do this in the future but for the time being is deemed too tricky
    if len(words) != 2:
        return []
    facts = []
    chunks = []
    chunk = []
    for word in words:
        if len(chunk) < 1:
            # I think this solves some edge cases but can't remember what
            # will add docs when I figure it out
            # if "." in word:
            #     word = word.split(".")[-1]
            chunk.append(word)
        else:
            # I think this solves some edge cases but can't remember what
            # will add docs when I figure it out
            # if "." in word:
            #     word = word.split(".")[0]
            chunk.append(word)
            chunks.append(chunk)
            chunk = [word]
    if any(chunks):
        print(f"chunks: {chunks}")
    for chunk in chunks:
        # Some sentences can be like "if a country is a member of NATO"
        # that contain conditional information.
        # This code used to change the relationship we were going to put into the
        # database from "is" to "can be" to reflect that it isn't always the case
        # TODO: Do some thinking about whether I want to do this and either resurrect it or delete it
        # join = "is"
        # if " if " in chunk[0] or " if:" in chunk[0]:
        #     join = "can be"
        subject_entity = ner.get_full_entity_for_word(sentence, chunk[0])
        if subject_entity and (pattern['any_subject_types'] or subject_entity['entity_type'] in pattern['subject_types']):
            object_entity = get_object_entity(ner, nlp, sentence, chunk[1], pattern)
            if object_entity:
                full_subject_entity = chunker.chunk(chunk[0], subject_entity['entity'])
                full_object_entity = chunker.chunk(chunk[1], object_entity['entity'])
                facts += CompoundObjectRelationshipExtractor(nlp).extract(sentence, full_object_entity)
                facts.append(Fact(full_subject_entity, full_object_entity, pattern['join'], sentence, pattern['has_direction'], pattern['direction_is_subject_to_object']))
    return facts

def get_object_entity(ner, nlp, sentence, object_entity_chunk, pattern):
    if 'object_regex' in pattern:
        doc = nlp(sentence)
        matches = list(textacy.extract.matches(doc, pattern['object_regex']))
        if any(matches):
            # Return longest
            return { 'entity': max(matches, key=len).text }
    else:
        object_entity = ner.get_full_entity_for_word(sentence, object_entity_chunk)
        if object_entity and (pattern['any_object_types'] or object_entity['entity_type'] in pattern['object_types']):
            return object_entity


def analyse(nlp, first_half_synthetic_sentence, synthetic_sentence):
    first_half_synthetic_sentence = first_half_synthetic_sentence.replace(" ", "")
    #     print(first_half_synthetic_sentence)
    #     print(sentence)
    pattern = build_action_sequences(nlp, synthetic_sentence)
    for key, value in pattern.items():
        print()
        print(value)
        lefts = [l.text for l in list(value['lefts']) if not l.text == value['head'][0]]
        print(lefts)
        l = "".join(lefts).replace(" ", "")
        print(f"l is {l}")
        if l == first_half_synthetic_sentence:
            print(f"IS A: {value['head'][0]}")
            return value['head'][0]


# Chunks up entities, for example:
# text: "NHS Continuing Healthcare is a package of care"
# we know the entity is NHS Contining Healthcare, but GovNER only
# knows 'NHS' is an entity and we want to get the whole thing
# Thus if we call EntityChunker(nlp).chunk(text, "NHS")
# we get 'NHS Continuing Healthcare'. Hooray
class EntityChunker:
    def __init__(self, nlp):
        self.nlp = nlp
    def chunk(self, full_sentence, known_chunk_entity):
        doc = self.nlp(full_sentence)
        for chunk in doc.noun_chunks:
            if known_chunk_entity in chunk.text:
                return chunk.text
        return known_chunk_entity


# Extracts compound nouns as facts about their relationship
# For example, the sentence "Social Work England is a specialist body"
# implies that a specialist body is a subclass of a body. Thus, it will return a fact like:
# (specialist body)<-[:SUBCLASS]-(body)
class CompoundObjectRelationshipExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
    def extract(self, full_sentence, object):
        doc = self.nlp(full_sentence)
        tokens = list(doc)
        object_parts = object.split(" ")
        compound_facts = []
        for i, token in enumerate(tokens):
            # If the word's text is in the object and it's a compound, the object might be compound
            print(f"{token.text}: {token.dep_}")
            if token.text in object and token.dep_ in ["compound", "amod"]:
                # Check that it's the word before the rest of the object
                # (eg that if the token.text is "specialist", then the next word must be "body")
                index_of_token_in_object = object_parts.index(token.text)
                next_word_in_object = object_parts[index_of_token_in_object + 1]
                next_word_in_sentence = tokens[i + 1].text
                if next_word_in_object == next_word_in_sentence:
                    beginning_of_this_object = " ".join(object_parts[index_of_token_in_object:])
                    rest_of_object = " ".join(object_parts[index_of_token_in_object + 1:])
                    compound_facts.append(Fact(beginning_of_this_object, rest_of_object, "SUBCLASS", full_sentence, True, False))
        return compound_facts

class Fact:
    def __init__(self, subject, object, relationship, extracted_from_sentence, has_direction, direction_is_subject_to_object):
        self.subject = subject
        self.object = object
        self.relationship = relationship
        self.extracted_from_sentence = extracted_from_sentence
        self.has_direction = has_direction
        self.direction_is_subject_to_object = direction_is_subject_to_object
    def __str__(self):
        if self.has_direction:
            return f"({self.subject}){'<' if not self.direction_is_subject_to_object else ''}-[:{self.relationship}]-{'>' if self.direction_is_subject_to_object else ''}({self.object})"
        return f"({self.subject})-[:{self.relationship}]-({self.object})"


