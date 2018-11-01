"""
Named Entity Recognition (NER)
"""
import spacy


nlp = spacy.load('pt_core_news_sm')

# Process whole documents
text = (u"O Ministério Público de Santa Catarina (MPSC) entrou"
        u" na Justiça com ação civil pública nesta terça-feira"
        u" (30) contra a deputada estadual eleita Ana Caroline"
        u" Campagnolo (PSL). O órgão quer a condenação por danos"
        u" morais coletivos e pede que seja dada liminar (decisão"
        u" temporária) para que ela se abstenha de manter qualquer"
        u" tipo de controle ideológico das atividades dos"
        u" professores e alunos de escolas públicas e privadas"
        u" do estado.")
doc = nlp(text)

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)
