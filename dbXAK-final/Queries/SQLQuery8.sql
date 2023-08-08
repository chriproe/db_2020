--8
CREATE VIEW services_sales AS 
SELECT
  a.ServiceDate,
  a.ServiceDescription,
  a.ServiceCost
FROM
  GetServCost a,
  Services b
WHERE 
  a.ID_Service = b.ID_Service 
--ORDER BY (b.ID_Service)
; 
 

CREATE VIEW customer_info AS
SELECT DISTINCT
  a.*,
  b.Phone,
  c.Email
FROM 
  Customers a
LEFT JOIN Phone b ON a.NFC_ID = b.NFC_ID
LEFT JOIN Email c ON a.NFC_ID = c.NFC_ID;