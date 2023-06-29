SELECT S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Note, SSP.Status, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester, AVG(SSP2.Note) AS Durchschnittsnote
FROM Student AS S, Student_schreibt_Pruefung AS SSP, Pruefung AS P
JOIN (
  SELECT *
  FROM Student_schreibt_Pruefung
  WHERE Note IS NOT NULL
) AS SSP2 ON SSP.Version = SSP2.Version AND SSP.Nummer = SSP2.Nummer AND SSP.Semesterjahr = SSP2.Semesterjahr AND SSP.Sommersemester = SSP2.Sommersemester
WHERE S.Pseudonym = 2754842
AND S.Pseudonym = SSP.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
GROUP BY S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester
ORDER BY SSP.Fachsemester
