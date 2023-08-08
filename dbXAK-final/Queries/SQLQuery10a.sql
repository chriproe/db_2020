SELECT DISTINCT Places.PlaceName, D.NumberofVisits
	
FROM
	Places, 
	(SELECT count(*) as NumberofVisits, ID_Place
	FROM 
		(SELECT Visit.NFC_ID, ID_Place, [VisitStartDate ], VisitEndDate
		FROM 
			Visit,
			(SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
					NFC_ID
			FROM Customers) ages
		WHERE 
			ages.Age BETWEEN 20 AND 40
		AND ages.NFC_ID = Visit.NFC_ID) Va
	GROUP BY ID_Place) D,

	(SELECT Visit.NFC_ID, ID_Place, [VisitStartDate ], VisitEndDate
		FROM 
			Visit,
			(SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
					NFC_ID
			FROM Customers) ages
		WHERE 
			ages.Age BETWEEN 20 AND 40
		AND ages.NFC_ID = Visit.NFC_ID) NewVisit

WHERE
	Places.ID_Place = NewVisit.ID_Place
	AND D.ID_Place = NewVisit.ID_Place
	AND MONTH(NewVisit.[VisitStartDate ]) = MONTH(GETDATE())
	AND YEAR(NewVisit.[VisitStartDate ]) = YEAR(GETDATE())

ORDER BY 
	NumberofVisits DESC


	
