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
CREATE TABLE ImagePersonHistory (
    sr_no INT PRIMARY KEY IDENTITY(1,1),
    image_id INT,
    person_id INT,
	version_no INT,
);

-- 6 Associative table for Image-Event relationship (many-to-many)
CREATE TABLE ImageEventHistory (
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
-----------------------------------------------------------new-------------------------------------------------
-- Insert records into LocationHistory table
INSERT INTO LocationHistory (id, name, latitude, longitude, version_no) VALUES
(1, 'Park', 40.712776, -74.005974, 1),
(2, 'Museum', 34.052235, -118.243683, 1),
(3, 'Library', 51.507351, -0.127758, 1),
(4, 'Cafe', 48.856613, 2.352222, 1);


-- Insert records into PersonHistory table
INSERT INTO PersonHistory (id, name, path, gender, version_no) VALUES
(1, 'Alina', '/images/alina.jpg', 'F', 1),
(2, 'Aliya', '/images/aliya.jpg', 'F', 1),
(3, 'Abeeha', '/images/abeeha.jpg', 'F', 1),
(4, 'Abeera', '/images/abeera.jpg', 'F', 1);

-- Insert records into EventHistory table
INSERT INTO EventHistory (id, name, version_no) VALUES
(1, 'Birthday Party', 1),
(2, 'Wedding', 1),
(3, 'Conference', 1),
(4, 'Picnic', 1);

-- Insert records into ImageHistory table
INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no) VALUES
(1, '/images/event1.jpg', 1, '2023-12-01', '2023-12-02', '2023-12-03', 1, 1),
(2, '/images/event2.jpg', 0, '2023-11-01', '2023-11-05', '2023-11-06', 2, 1),
(3, '/images/event3.jpg', 1, '2023-10-01', '2023-10-10', '2023-10-11', 3, 1),
(4, '/images/event4.jpg', 0, '2023-09-01', '2023-09-15', '2023-09-16', 4, 1);


-- Insert records into ImagePersonHistory table
INSERT INTO ImagePersonHistory (image_id, person_id, version_no) VALUES
(1, 1, 1),  -- Alina linked to image 1
(1, 2, 1),  -- Aliya linked to image 1
(2, 3, 1),  -- Abeeha linked to image 2
(3, 4, 1);  -- Abeera linked to image 3

-- Insert records into ImageEventHistory table
INSERT INTO ImageEventHistory (image_id, event_id, version_no) VALUES
(1, 1, 1),  -- Image 1 linked to Birthday Party
(2, 2, 1),  -- Image 2 linked to Wedding
(3, 3, 1),  -- Image 3 linked to Conference
(4, 4, 1);  -- Image 4 linked to Picnic

-- Insert records into LinkHistory table
INSERT INTO LinkHistory (person1_id, person2_id, version_no) VALUES
(1, 2, 1),  -- Alina and Aliya are linked
(1, 3, 1),  -- Alina and Abeeha are linked
(2, 4, 1),  -- Aliya and Abeera are linked
(3, 4, 1);  -- Abeeha and Abeera are linked
