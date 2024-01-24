SELECT S.Pseudonym, SSP.Sommersemester, SSP.Fachsemester, SSP.Semesterjahr, E.Studienfach, E.Abschluss, SSP.ECTS, P.Modul, S.Geschlecht, S.Deutsch
FROM Student as S, Einschreibung as E, Student_schreibt_Pruefung as SSP, Pruefung as P
WHERE S.Pseudonym = E.Pseudonym
AND SSP.Pseudonym = S.Pseudonym
AND P.Version = SSP.Version
AND P.Nummer = SSP.Nummer
