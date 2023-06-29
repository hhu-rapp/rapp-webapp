SELECT S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Note, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester, AVG(SSP2.Note) AS Durchschnittsnote
FROM Student AS S, Student_schreibt_Pruefung AS SSP, Pruefung AS P
JOIN (
  SELECT *
  FROM Student_schreibt_Pruefung
  WHERE Note > 0 AND Note IS NOT NULL
) AS SSP2 ON SSP.Version = SSP2.Version AND SSP.Nummer = SSP2.Nummer
WHERE S.Pseudonym = 3970913
AND S.Pseudonym = SSP.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
GROUP BY S.Pseudonym, SSP.Studienfach, SSP.Version, SSP.Nummer, P.Modul, SSP.ECTS, SSP.Versuch, SSP.Fachsemester, SSP.Hochschulsemester
