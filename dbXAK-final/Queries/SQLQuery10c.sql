SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsedDiffCustomer
	
FROM
	Services, 
	(SELECT count(DISTINCT NFC_ID) as NumberofTimesUsedDiffCustomer, ID_Service
	FROM 
		(SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
		FROM 
			GetServCost,
			(SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
					NFC_ID
			FROM Customers) ages
		WHERE 
			ages.Age BETWEEN 20 AND 40
		AND ages.NFC_ID = GetServCost.NFC_ID) Va
	GROUP BY ID_Service) D,

	(SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
		FROM 
			GetServCost,
			(SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
					NFC_ID
			FROM Customers) ages
		WHERE 
			ages.Age BETWEEN 20 AND 40
		AND ages.NFC_ID = GetServCost.NFC_ID) NewServ

WHERE
	Services.ID_Service = NewServ.ID_Service
	AND D.ID_Service = NewServ.ID_Service
	AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())
	AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())

ORDER BY 
	NumberofTimesUsedDiffCustomer DESC