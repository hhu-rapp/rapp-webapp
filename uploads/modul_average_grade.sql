SELECT P.Modul, AVG(SSP.Note) AS Durchschnittsnote
FROM Student_schreibt_Pruefung AS SSP, Pruefung AS P
WHERE P.Modul = :modul
AND SSP.Note IS NOT NULL
