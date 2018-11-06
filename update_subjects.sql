-- Jornal de SC
UPDATE news SET subject = 'Mundo'
WHERE portal = 'Jornal de SC' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND tags LIKE '%mundo%';

UPDATE news SET subject = 'Esporte'
WHERE portal = 'Jornal de SC' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND tags LIKE '%sporte%';

UPDATE news SET subject = 'Saúde'
WHERE portal = 'Jornal de SC' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND tags LIKE '%aúde%';


-- RIC MAIS
UPDATE news SET subject = 'Esporte'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (subject = 'Esportes');

UPDATE news SET subject = 'Política'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%olítica%' OR tags LIKE '%leiç%' OR tags LIKE '%leic%');

UPDATE news SET subject = 'Mundo'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%xterior%');

UPDATE news SET subject = 'Economia'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%conomia%');

UPDATE news SET subject = 'Clima'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%tempo%');

UPDATE news SET subject = 'Sem Classificação'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (subject = 'Entretenimento' OR subject = 'Jornalismo');

UPDATE news SET subject = 'Política'
WHERE portal = 'RIC MAIS' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%debate%');


-- NDONLINE
UPDATE news SET subject = 'Sem Classificação'
WHERE portal = 'NDONLINE' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND subject IN ('Geral', 'Cidade', 'Estado', 'Região', 'Tecnologia');

UPDATE news SET subject = 'Política'
WHERE portal = 'NDONLINE' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND subject IN ('Eleições 2018', 'Direitos Humanos');

UPDATE news SET subject = 'Segurança'
WHERE portal = 'NDONLINE' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (subject = 'Justiça' OR
tags LIKE '%crime%' OR tags LIKE '%facada%' OR tags LIKE '%feminicídio%' OR
tags LIKE '%tiro%' OR tags LIKE '%vitima%' OR tags LIKE '%atropelam%' OR
tags LIKE '%roubo%' OR tags LIKE '%homicidio%' OR tags LIKE '%droga%');

UPDATE news SET subject = 'Esporte'
WHERE portal = 'NDONLINE' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%sporte%' OR tags LIKE '%utebol%');


-- Globo G1
UPDATE news SET subject = 'Sem Classificação'
WHERE portal = 'Globo G1' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';

UPDATE news SET subject = 'Política'
WHERE portal = 'Globo G1' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%Andreá Luciano Carvalho%' OR tags LIKE '%Diego Mezzogiorno%' OR
tags LIKE '%Esperidião Amin%' OR tags LIKE '%Ideli Salvatti%' OR tags LIKE '%Jorginho Mello%' OR tags LIKE '%Lucas Esmeraldino%' OR
tags LIKE '%Lédio Rosa%' OR tags LIKE '%Miriam Prochnow%' OR tags LIKE '%PCO%' OR
tags LIKE '%PMN%' OR tags LIKE '%PP%' OR tags LIKE '%PR%' OR tags LIKE '%PSD%' OR tags LIKE '%PSDB%' OR tags LIKE '%PSL%' OR
tags LIKE '%PSOL%' OR tags LIKE '%PSTU%' OR tags LIKE '%PT%' OR tags LIKE '%Paulo Bauer%' OR
tags LIKE '%MDB%' OR tags LIKE '%Merísio%' OR tags LIKE '%Mariani%' OR tags LIKE '%Bolsonaro%' OR tags LIKE '%Moisés%' OR tags LIKE '%Haddad%' OR
tags LIKE '%Eleitoral%' OR tags LIKE '%Décio Lima%' OR tags LIKE '%Patriota%');

UPDATE news SET subject = 'Segurança'
WHERE portal = 'Globo G1' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND (tags LIKE '%olícia%');


-- DIARIO CATARINENSE
UPDATE news SET subject = 'Segurança'
WHERE portal = 'DIARIO CATARINENSE' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018'
AND subject = 'Polícia';


-- Translate topics to English
UPDATE news SET subject = 'Economy' WHERE subject = 'Economia' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Health' WHERE subject = 'Saúde' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Politics' WHERE subject = 'Política' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Sports' WHERE subject = 'Esporte' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Public Safety' WHERE subject = 'Segurança' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'World' WHERE subject = 'Mundo' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Unclassified' WHERE subject = 'Sem Classificação' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';
UPDATE news SET subject = 'Weather' WHERE subject = 'Clima' AND date_time <= '22/10/2018' AND date_time >= '22/09/2018';