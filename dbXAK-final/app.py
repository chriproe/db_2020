import os
import re
from datetime import datetime

import pypyodbc
from flask import Flask, render_template, request

app = Flask(__name__)

sql_user = 'sa'
sql_password = 'kostas'
sql_server_name = 'LAPTOP-6U0THMK4\SQLEXPRESS' 
sql_database_name = 'dbXAK'
connection = pypyodbc.connect('Driver={SQL Server};Server='+sql_server_name+';Database='+sql_database_name+';uid='+sql_user+';pwd='+sql_password)

@app.route('/', methods = ["GET", "POST"])
def Home():
    return render_template("Home.html")


@app.route('/Tracing', methods = ["GET", "POST"])
def Covid_Cases():
    rs = connection.cursor() 
    query_nfc = "SELECT NFC_ID FROM Customers"
    rs.execute(query_nfc)
    customer_nfc = rs.fetchall()
    NFC = str(request.form.get("nfc"))
    if NFC == 'None':
        NFC = ""
    query_plausible_cases = """SELECT DISTINCT
    plausible.NFC_ID
    FROM
    (SELECT * FROM Visit Positive_Case WHERE Positive_Case.NFC_ID = '{}') AS positive, 
    (SELECT * FROM Visit Plausible_Case WHERE Plausible_Case.NFC_ID != '{}') AS plausible  
    WHERE
    plausible.ID_Place = positive.ID_Place
    AND (plausible.[VisitStartDate ] >= positive.[VisitStartDate ]
    AND plausible.[VisitStartDate ] <= positive.[VisitEndDate]+0.041666666
    OR plausible.VisitEndDate >= positive.[VisitStartDate ]
    AND plausible.VisitEndDate <= positive.[VisitEndDate]+0.041666666)
    """.format(NFC, NFC)
    rs.execute(query_plausible_cases)
    results = rs.fetchall()
    query_places = """SELECT 
    *
    FROM
    Visit 
    WHERE
    NFC_ID = '{}'
    ORDER BY (VisitStartDate) DESC; 
    """.format(NFC)
    rs.execute(query_places)
    places = rs.fetchall()
    return render_template("Tracing.html", customer_nfc = customer_nfc, results = results, NFC = NFC, places = places)
    
@app.route('/Search', methods = ["GET", "POST"])
def Search():
    rs = connection.cursor() 
    month = str(request.form.get("month"))
    year = str(request.form.get("year"))
    service = str(request.form.get("service"))
    cost = str(request.form.get("cost"))
    if month == 'None':
        month = ""
    if year == 'None':
        year = ""
    if service == 'None':
        sevice = ""
    if cost == 'None':
        cost = ""
    query_search = """SELECT
    GetServCost.ID_Service,
    GetServCost.ServiceDescription, 
    GetServCost.NFC_ID,
    GetServCost.ServiceDate,
    GetServCost.ServiceCost  
    FROM 
    Services,
    GetServCost
    WHERE 
    GetServCost.ID_Service = Services.ID_Service"""
    if month != "":
        query_search = query_search + " AND MONTH(GetServCost.ServiceDate) = '{}'".format(month)
    if year != "":
        query_search = query_search + " AND YEAR(GetServCost.ServiceDate)  = '{}'".format(year)
    if service != "":
        query_search = query_search + " AND GetServCost.ServiceDescription = '{}'".format(service)
    if cost != "":
        query_search = query_search + " AND GetServCost.ServiceCost = '{}'".format(cost) 
    rs.execute(query_search)
    results = rs.fetchall()
    return render_template("Search.html", results = results)
    
@app.route('/customer_info', methods = ["GET", "POST"])
def View1():
    rs = connection.cursor()
    myquery_view1 = """SELECT * FROM customer_info"""
    rs.execute(myquery_view1)
    results = rs.fetchall()
    return render_template("customer_info.html", results = results)


@app.route('/services_sales', methods = ["GET", "POST"])
def View2():
    rs = connection.cursor()
    myquery_view2 = """SELECT * FROM services_sales ORDER BY ServiceDate"""
    rs.execute(myquery_view2)
    results = rs.fetchall()
    return render_template("services_sales.html", results = results)

@app.route('/AgeGroup1', methods = ["GET", "POST"])
def AgeGroup1():
    rs = connection.cursor()
    time_period = str(request.form.get("time_period"))
    myquery_AgeGroup1 = """SELECT DISTINCT Places.PlaceName, D.NumberofVisits
	
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
        AND D.ID_Place = NewVisit.ID_Place"""
    if time_period == "Last Month":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND MONTH(NewVisit.[VisitStartDate ]) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND YEAR(NewVisit.[VisitStartDate ]) = YEAR(GETDATE())"
    myquery_AgeGroup1 = myquery_AgeGroup1 + " ORDER BY NumberofVisits DESC"
    rs.execute(myquery_AgeGroup1)
    results = rs.fetchall()
    myquery_AgeGroup1_Services ="""SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsed
        
        FROM
        Services, 
        (SELECT count(*) as NumberofTimesUsed, ID_Service
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
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " ORDER BY NumberofTimesUsed DESC"
    rs.execute(myquery_AgeGroup1_Services)
    results2 = rs.fetchall()
    myquery_AgeGroup1_Services2 = """SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsedDiffCustomer
	
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
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " ORDER BY NumberofTimesUsedDiffCustomer DESC"
    rs.execute(myquery_AgeGroup1_Services2)
    results3 = rs.fetchall()
    return render_template("AgeGroup1.html", results = results, taim = time_period, results2 = results2, results3 = results3)

@app.route('/AgeGroup2', methods = ["GET", "POST"])
def AgeGroup2():
    rs = connection.cursor()
    time_period = str(request.form.get("time_period"))
    myquery_AgeGroup1 = """SELECT DISTINCT Places.PlaceName, D.NumberofVisits
	
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
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = Visit.NFC_ID) Va
        GROUP BY ID_Place) D,

        (SELECT Visit.NFC_ID, ID_Place, [VisitStartDate ], VisitEndDate
            FROM 
                Visit,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = Visit.NFC_ID) NewVisit

    WHERE
        Places.ID_Place = NewVisit.ID_Place
        AND D.ID_Place = NewVisit.ID_Place"""
    if time_period == "Last Month":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND MONTH(NewVisit.[VisitStartDate ]) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND YEAR(NewVisit.[VisitStartDate ]) = YEAR(GETDATE())"
    myquery_AgeGroup1 = myquery_AgeGroup1 + " ORDER BY NumberofVisits DESC"
    rs.execute(myquery_AgeGroup1)
    results = rs.fetchall()
    myquery_AgeGroup1_Services ="""SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsed
        
        FROM
        Services, 
        (SELECT count(*) as NumberofTimesUsed, ID_Service
        FROM 
            (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = GetServCost.NFC_ID) Va
        GROUP BY ID_Service) D,

        (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = GetServCost.NFC_ID) NewServ

        WHERE
        Services.ID_Service = NewServ.ID_Service
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " ORDER BY NumberofTimesUsed DESC"
    rs.execute(myquery_AgeGroup1_Services)
    results2 = rs.fetchall()
    myquery_AgeGroup1_Services2 = """SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsedDiffCustomer
	
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
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = GetServCost.NFC_ID) Va
        GROUP BY ID_Service) D,

        (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 41 AND 60
            AND ages.NFC_ID = GetServCost.NFC_ID) NewServ

    WHERE
        Services.ID_Service = NewServ.ID_Service
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " ORDER BY NumberofTimesUsedDiffCustomer DESC"
    rs.execute(myquery_AgeGroup1_Services2)
    results3 = rs.fetchall()
    return render_template("AgeGroup2.html", results = results, taim = time_period, results2 = results2, results3 = results3)

@app.route('/AgeGroup3', methods = ["GET", "POST"])
def AgeGroup3():
    rs = connection.cursor()
    time_period = str(request.form.get("time_period"))
    myquery_AgeGroup1 = """SELECT DISTINCT Places.PlaceName, D.NumberofVisits
	
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
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = Visit.NFC_ID) Va
        GROUP BY ID_Place) D,

        (SELECT Visit.NFC_ID, ID_Place, [VisitStartDate ], VisitEndDate
            FROM 
                Visit,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = Visit.NFC_ID) NewVisit

    WHERE
        Places.ID_Place = NewVisit.ID_Place
        AND D.ID_Place = NewVisit.ID_Place"""
    if time_period == "Last Month":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND MONTH(NewVisit.[VisitStartDate ]) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1 = myquery_AgeGroup1 + " AND YEAR(NewVisit.[VisitStartDate ]) = YEAR(GETDATE())"
    myquery_AgeGroup1 = myquery_AgeGroup1 + " ORDER BY NumberofVisits DESC"
    rs.execute(myquery_AgeGroup1)
    results = rs.fetchall()
    myquery_AgeGroup1_Services ="""SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsed
        
        FROM
        Services, 
        (SELECT count(*) as NumberofTimesUsed, ID_Service
        FROM 
            (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = GetServCost.NFC_ID) Va
        GROUP BY ID_Service) D,

        (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = GetServCost.NFC_ID) NewServ

        WHERE
        Services.ID_Service = NewServ.ID_Service
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services = myquery_AgeGroup1_Services + " ORDER BY NumberofTimesUsed DESC"
    rs.execute(myquery_AgeGroup1_Services)
    results2 = rs.fetchall()
    myquery_AgeGroup1_Services2 = """SELECT DISTINCT Services.ServiceDescription, D.NumberofTimesUsedDiffCustomer
	
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
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = GetServCost.NFC_ID) Va
        GROUP BY ID_Service) D,

        (SELECT GetServCost.NFC_ID, ID_Service, ServiceDate
            FROM 
                GetServCost,
                (SELECT DATEDIFF(year, Customers.BirthDate, GETDATE()) as Age,
                        NFC_ID
                FROM Customers) ages
            WHERE 
                ages.Age BETWEEN 61 AND 120
            AND ages.NFC_ID = GetServCost.NFC_ID) NewServ

    WHERE
        Services.ID_Service = NewServ.ID_Service
        AND D.ID_Service = NewServ.ID_Service"""
    if time_period == "Last Month":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND MONTH(NewServ.ServiceDate) = MONTH(GETDATE())"
    if time_period == "Last Year":
        myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " AND YEAR(NewServ.ServiceDate) = YEAR(GETDATE())"
    myquery_AgeGroup1_Services2 = myquery_AgeGroup1_Services2 + " ORDER BY NumberofTimesUsedDiffCustomer DESC"
    rs.execute(myquery_AgeGroup1_Services2)
    results3 = rs.fetchall()
    return render_template("AgeGroup3.html", results = results, taim = time_period, results2 = results2, results3 = results3)
