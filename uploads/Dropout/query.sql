SELECT
-- Features
--
--
-- protected attributes
S.Geschlecht,
S.Deutsch,
strftime("%Y", E.Immatrikulationsdatum) - S.Geburtsjahr as AlterEinschreibung,
--
SUM(CASE WHEN SSP.Fachsemester = 1 THEN SSP.ECTS ELSE 0 END) as EctsFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END ) as ExamsFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
           THEN SSP.Pseudonym ELSE null END ) as PassedFirstTerm,
COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status <> 'bestanden'
           THEN SSP.Pseudonym ELSE null END ) as FailedFirstTerm,
-- Ratio of passed exams; zero if none attempted.
CASE WHEN COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END) = 0
     THEN 0.0
     ELSE (
       COUNT(CASE WHEN SSP.Fachsemester = 1 AND SSP.Status = 'bestanden'
             THEN SSP.Pseudonym ELSE null END )
       * 1. / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END)
     )
     END as PassedExamsRatio,
IFNULL(SUM(CASE WHEN SSP.Fachsemester = 1 THEN SSP.ECTS ELSE 0 END) * 1.
        / COUNT(CASE WHEN SSP.Fachsemester = 1 THEN SSP.Pseudonym ELSE null END),
       0)
  as EctsPerExam,
-- Labels
Dropout.Dropout
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E

INNER JOIN
  (SELECT
    S.Pseudonym,
    E.Studienfach,
    E.Abschluss,
    -- E.Bestanden,
    -- LetztePruefung.SemesterCode,
    CASE WHEN LetztePruefung.SemesterCode < 20192 THEN NOT E.Bestanden ELSE null END as Dropout
    -- 20192 is the code for wintersemester 2019 (summersemester would be 20191).
    -- This is three terms ago, given the age of the dataset.
    -- Thus, everybody not writing an exam in the last three terms is assumed
    -- to have ended their studyship, and those whom did not graduate are deemed
    -- as dropouts.
  FROM
    Student as S,
    Einschreibung as E
  JOIN
    (SELECT
      SSP.Pseudonym,
      max(SSP.Semesterjahr*10 + (2-SSP.Sommersemester)) as SemesterCode
    FROM
      Student_schreibt_Pruefung as SSP
    GROUP BY SSP.Pseudonym
    ) as LetztePruefung
    ON S.Pseudonym = LetztePruefung.Pseudonym
  WHERE S.Pseudonym = E.Pseudonym
  ) as Dropout ON Dropout.Pseudonym = S.Pseudonym
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
AND Dropout.Studienfach = E.Studienfach
AND Dropout.Abschluss = E.Abschluss
AND Dropout.Dropout IN (0, 1)  -- NULL-Entries are sorted out
GROUP BY S.Pseudonym
