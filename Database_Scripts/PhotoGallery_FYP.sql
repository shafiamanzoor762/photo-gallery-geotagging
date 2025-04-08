-- 1 Table for Location entity
CREATE TABLE Location (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    name VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- 2 Table for Person entity
CREATE TABLE Person (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    name VARCHAR(255),
    path VARCHAR(255),
	gender CHAR(1) CHECK (Gender IN ('M', 'F'))
);

ALTER TABLE Person 
ADD CONSTRAINT CK_Person_Genderr CHECK (gender IN ('M', 'F', 'U'));


-- 3 Table for Event entity
CREATE TABLE Event (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    name VARCHAR(255)
);

-- 4 Table for Image entity
CREATE TABLE Image (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    path VARCHAR(255) NOT NULL,
    is_sync BIT,  -- Using BIT instead of BOOLEAN
    capture_date DATE,
    event_date DATE,  -- Event date
    last_modified DATE,
    location_id INT,  -- Define location_id column for foreign key reference
    CONSTRAINT FK_Image_Location FOREIGN KEY (location_id) REFERENCES Location(id)
);

-- 5 Associative table for Image-Person relationship (many-to-many)
CREATE TABLE ImagePerson (
    image_id INT,
    person_id INT,
    PRIMARY KEY (image_id, person_id),
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (person_id) REFERENCES Person(id)
);

-- 6 Associative table for Image-Event relationship (many-to-many)
CREATE TABLE ImageEvent (
    image_id INT,
    event_id INT,
    PRIMARY KEY (image_id, event_id),
    FOREIGN KEY (image_id) REFERENCES Image(id),
    FOREIGN KEY (event_id) REFERENCES Event(id)
);

--7 Link Table (NEW)
Create TABLE Link(
    person1_id INT,
    person2_id INT,
    PRIMARY KEY (person1_id, person2_id),
    FOREIGN KEY (person1_id) REFERENCES Person(id),
    FOREIGN KEY (person2_id) REFERENCES Person(id)
);
