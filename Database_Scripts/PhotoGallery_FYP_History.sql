-- 1 Table for Location entity
CREATE TABLE LocationHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
	version_no INT,
);
ALTER TABLE LocationHistory
ADD is_Active bit Not NULL DEFAULT 0;

-- 2 Table for Person entity
CREATE TABLE PersonHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
    path VARCHAR(255),
	gender CHAR(1) CHECK (Gender IN ('M', 'F','U')),
	version_no INT,
);
ALTER TABLE PersonHistory
ADD is_Active bit Not NULL DEFAULT 0;
ALTER TABLE Person 
ADD CONSTRAINT CK_Person_Gender CHECK (gender IN ('M', 'F', 'U'));

-- 3 Table for Event entity
CREATE TABLE EventHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
	version_no INT,
);
ALTER TABLE EventHistory
ADD is_Active bit Not NULL DEFAULT 0;

-- 4 Table for Image entity
CREATE TABLE ImageHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    path VARCHAR(255) NOT NULL,
    is_sync BIT,  -- Using BIT instead of BOOLEAN
    capture_date DATE,
    event_date DATE,  -- Event date
    last_modified DATE,
    location_id INT,
	version_no INT,
);
ALTER TABLE imagehistory
ADD is_deleted BIT NOT NULL DEFAULT 0;
ALTER TABLE ImageHistory
ADD hash VARCHAR(64) NOT NULL;
ALTER TABLE ImageHistory
ADD is_Active bit Not NULL DEFAULT 0;
ALTER TABLE imageHistory
ALTER COLUMN last_modified DATETIME;
Alter table ImageHistory
Add created_at DATE;


--for undo add created_at column

ALTER TABLE personHistory
ADD created_at DATETIME DEFAULT GETDATE();

-- 5 Associative table for Image-Person relationship (many-to-many)
CREATE TABLE ImagePersonHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    image_id INT,
    person_id INT,
	version_no INT,
);
ALTER TABLE ImagePersonHistory
ADD is_Active bit Not NULL DEFAULT 0;
Alter table PersonHistory
Add created_at DATE;

-- 6 Associative table for Image-Event relationship (many-to-many)
CREATE TABLE ImageEventHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    image_id INT,
    event_id INT,
	version_no INT,
);
ALTER TABLE ImageEventHistory
ADD is_Active bit Not NULL DEFAULT 0;
Alter table ImageEventHistory
Add created_at DATE;

--7 Link Table (NEW)
Create TABLE LinkHistory(
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    person1_id INT,
    person2_id INT,
    version_no INT,
);
ALTER TABLE LinkHistory
ADD is_Active bit Not NULL DEFAULT 0;