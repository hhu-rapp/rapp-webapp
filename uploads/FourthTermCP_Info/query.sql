SELECT
-- Features
S.Pseudonym,
--
--
-- protected attributes
S.Geschlecht,
S.Deutsch,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
FirstTermData.Ectp,
FirstTermData.KlausurenGeschrieben,
FirstTermData.KlausurenBestanden,
FirstTermData.KlausurenNichtBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteBestanden IS NULL
     then 5 else FirstTermData.DurchschnittsNoteBestanden end as DurchschnittsnoteBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteTotal IS NULL
     then 5 else FirstTermData.DurchschnittsNoteTotal end as DurchschnittsnoteTotal,
CASE WHEN FirstTermData.DurchschnittsNoteBestanden IS NULL
     then 0 else
  (SUM(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden'
      THEN (SSP.NOTE-FirstTermData.DurchschnittsNoteBestanden)*(SSP.NOTE-FirstTermData.DurchschnittsNoteBestanden)
      ELSE NULL END)
    / FirstTermData.KlausurenBestanden)
END as VarianzNoteBestanden,
CASE WHEN FirstTermData.DurchschnittsNoteTotal IS NULL
     then 0 else
  (SUM ((SSP.NOTE-FirstTermData.DurchschnittsNoteTotal)
        * (SSP.NOTE-FirstTermData.DurchschnittsNoteTotal))
    / FirstTermData.KlausurenGeschrieben)
END as VarianzNoteTotal,
-- Ratio of passed exams; zero if none attempted.
CASE WHEN COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END) = 0
     THEN 0.0
     ELSE (
       COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
             THEN SSP.Pseudonym ELSE null END )
       * 1. / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END)
     )
     END as PassedExamsRatio,
IFNULL(FirstTermData.Ectp*1./FirstTermData.KlausurenGeschrieben,
       0) as EctpPerExam,
-- Labels
--  Whether the students achieve sufficient credits after four semesters.
--  Sufficient is defined as 100: 30 CP per semester adds up to 120 CP after
--  four semesters. We give 20 CP wiggle room.
case when SUM(CASE WHEN SSP.Fachsemester <= 4 THEN SSP.ECTS ELSE 0 END) >= 100
  then 1 else 0 end as FourthTermCP
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
LEFT JOIN
  (SELECT -- FirstTermData
    SSP.Pseudonym,
    SUM(SSP.ECTS) as Ectp,
    AVG(CASE WHEN SSP.Note <> 0 AND SSP.Status = 'bestanden'
        THEN SSP.NOTE ELSE null END) as DurchschnittsNoteBestanden,
    AVG(SSP.NOTE) as DurchschnittsNoteTotal,
    COUNT(SSP.Pseudonym) as KlausurenGeschrieben,
    COUNT(CASE WHEN SSP.Status = 'bestanden'
               THEN SSP.Pseudonym ELSE null END ) as KlausurenBestanden,
    COUNT(CASE WHEN SSP.Status <> 'bestanden'
               THEN SSP.Pseudonym ELSE null END ) as KlausurenNichtBestanden
  FROM
    Student_schreibt_Pruefung as SSP
  WHERE SSP.Studienfach = "Informatik"
    AND SSP.Abschluss = "Bachelor"
    AND SSP.Fachsemester = 1
  GROUP BY SSP.Pseudonym
  HAVING KlausurenGeschrieben > 0 -- Ignore entries with no recorded first semester.
  ) as FirstTermData
  ON FirstTermData.Pseudonym = SSP.Pseudonym

WHERE
    S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
AND E.Studienfach = "Informatik"
AND E.Abschluss = "Bachelor"
AND SSP.Fachsemester = 1
AND SSP.Studienfach = E.Studienfach
AND SSP.Abschluss = E.Abschluss
-- Only consider since PO 2007
AND '2007-01-01' <= date(E.Immatrikulationsdatum)

GROUP BY S.Pseudonym

