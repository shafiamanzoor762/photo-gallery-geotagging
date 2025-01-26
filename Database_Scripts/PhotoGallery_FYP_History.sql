-- 1 Table for Location entity
CREATE TABLE LocationHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
	version_no INT,
);

-- 2 Table for Person entity
CREATE TABLE PersonHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
    path VARCHAR(255),
	gender CHAR(1) CHECK (Gender IN ('M', 'F')),
	version_no INT,
);

-- 3 Table for Event entity
CREATE TABLE EventHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    id INT,
    name VARCHAR(255),
	version_no INT,
);

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

-- 5 Associative table for Image-Person relationship (many-to-many)
CREATE TABLE Image_PersonHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    image_id INT,
    person_id INT,
	version_no INT,
);

-- 6 Associative table for Image-Event relationship (many-to-many)
CREATE TABLE Image_EventHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    image_id INT,
    event_id INT,
	version_no INT,
);

--7 Link Table (NEW)
Create TABLE LinkHistory(
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    person1_id INT,
    person2_id INT,
    version_no INT,
);
