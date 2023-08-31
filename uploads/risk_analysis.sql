SELECT S.Pseudonym , S.Geschlecht, S.Deutsch, E.Abschluss, E.Studienfach
FROM Student as S, Einschreibung as E
WHERE S.Pseudonym = E.Pseudonym
