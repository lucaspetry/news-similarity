import pandas as pd
import news_loader as nl
from news_loader import load_news
from news_loader import load_distinct
import spacy
from spacy import displacy
from scipy.spatial import distance

##################################
# Get entities from a text
##################################

def get_entities(text):
	nlp = spacy.load('pt')
	nlp_text = nlp(text)
	return nlp_text.ents

def get_news():
	news = nl.load_news(fields=['id', 'title', 'portal', 'text'])
	return news

def get_portals():
	portals = nl.load_distinct('portal')
	return portals

def entities_to_lower(tuples):

	ents = list(tuples)
	ret_val = []
	for en  in ents:
		ret_val.append(str(en).lower())

	return set(ret_val)

def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    print(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)

news = get_news()
ent_dict = dict()

print("Starting Entities Extraction")

for article in news:
	news_id = article['id']
	news_text = article['text']

	ent_dict[news_id] = list(entities_to_lower(get_entities(news_text)))

print("Entities Extraction Done")

print("Starting Jaccard Calculation")

for new_id_first in ent_dict:
	for new_id_sec in ent_dict:
		
		if new_id_first == new_id_sec or new_id_first > new_id_sec:
			continue

		jaccard = jaccard_similarity(ent_dict[new_id_first], ent_dict[new_id_sec])

		if jaccard > 0.1:
			add_score([new_id_first, new_id_sec], 'score_jaccard_ner', jaccard)



