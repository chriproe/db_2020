--7
SELECT
  Services.ID_Service,
  Services.ServiceDescription, 
  GetServCost.NFC_ID,
  GetServCost.ID_Service,
  GetServCost.ServiceDate,
  GetServCost.ServiceDescription,
  GetServCost.ServiceCost  
FROM 
  Services,
  GetServCost
WHERE 
  GetServCost.ID_Service = Services.ID_Service
  AND MONTH(GetServCost.ServiceDate) = MONTH('2021-06-15 11:40:00.00')
  AND YEAR(GetServCost.ServiceDate)  = YEAR('2021/06/15')
  AND GetServCost.ServiceDescription = 'Spa'
  AND GetServCost.ServiceCost = '5'
  ;

