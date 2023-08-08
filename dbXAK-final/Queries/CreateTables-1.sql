USE MASTER
GO
CREATE DATABASE dbXAK

USE dbXAK
GO

-- Table Structure for table 'Customers'
CREATE TABLE Customers
(
--NFC_ID int NOT NULL IDENTITY (1,1) PRIMARY KEY,
NFC_ID int NOT NULL PRIMARY KEY,
FirstName varchar(255),
LastName varchar(255),
BirthDate Date,
ID_Number varchar(255),
ID_Type varchar(255),
ID_Place varchar(255)
)

-- Table Structure for table 'Phone'
CREATE TABLE Phone
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
Phone bigint NOT NULL,
CONSTRAINT PKPhone PRIMARY KEY (NFC_ID, Phone)
)

-- Table Structure for table 'Email'
CREATE TABLE Email
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
Email varchar(255) NOT NULL,
CONSTRAINT PKEmail PRIMARY KEY (NFC_ID, Email)
)

-- Table Structure for table 'Places'
CREATE TABLE Places
(
ID_Place int NOT NULL IDENTITY (1,1) PRIMARY KEY,
--ID_Place int NOT NULL PRIMARY KEY,
BedsNumber int,
PlaceName varchar(255),
PlaceDescription varchar(255)
)

-- Table Structure for table 'Services'
CREATE TABLE Services 
(
ID_Service int NOT NULL IDENTITY (1,1) PRIMARY KEY,
--ID_Service int NOT NULL PRIMARY KEY,
ServiceDescription varchar(255),
ServiceSubscription bit
)


--Table Structure for table 'Access'
CREATE TABLE Access
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
ID_Place int NOT NULL FOREIGN KEY REFERENCES Places(ID_Place),
AccessStartDate DateTime,
AccessEndDate DateTime,
CONSTRAINT PKAccess PRIMARY KEY (NFC_ID, ID_place),


-- Table Structure for table 'Visit'
CREATE TABLE Visit
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
ID_Place int NOT NULL FOREIGN KEY REFERENCES Places(ID_Place),
VisitStartDate DateTime NOT NULL,
VisitEndDate DateTime NOT NULL,
CONSTRAINT PKVisit PRIMARY KEY (NFC_ID, ID_Place, VisitStartDate),

)

-- Table Structure for table 'GetService'
CREATE TABLE GetServCost
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
ServiceDate DateTime,
ID_Service int NOT NULL FOREIGN KEY REFERENCES Services(ID_Service),
ServiceDescription varchar (255),
ServiceCost int,
CONSTRAINT PKGetService PRIMARY KEY (NFC_ID, ServiceDate, ID_Service)
)

-- Table Structure for table 'SubscribeService'
CREATE TABLE SubscribeService
(
NFC_ID int NOT NULL FOREIGN KEY REFERENCES Customers(NFC_ID),
ID_Service int NOT NULL FOREIGN KEY REFERENCES Services(ID_Service),
SubscriptionDate DateTime NOT NULL,
CONSTRAINT PKSubscribeService PRIMARY KEY(NFC_ID, ID_Service)
)

-- Table Structure for table 'AvailabeAt'
CREATE TABLE AvailableAt
(
ID_Place int NOT NULL FOREIGN KEY REFERENCES Places(ID_Place),
ID_Service int NOT NULL FOREIGN KEY REFERENCES Services(ID_Service)
CONSTRAINT PKAvailableAt PRIMARY KEY (ID_Place, ID_Service)












