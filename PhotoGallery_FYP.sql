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
    path VARCHAR(255)
);
ALTER TABLE Person
ADD Gender CHAR(1) CHECK (Gender IN ('M', 'F')) NOT NULL;

-- 3 Table for Event entity
CREATE TABLE Event (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    name VARCHAR(255)
);

-- 4 Table for Image entity
CREATE TABLE Image (
    id INT PRIMARY KEY IDENTITY(1,1),  -- Auto-increment primary key
    path VARCHAR(255) NOT NULL,
    isSync BIT,  -- Using BIT instead of BOOLEAN
    captureDate DATE,
    EventDate DATE,  -- Event date
    lastModified DATE,
    location_id INT,  -- Define location_id column for foreign key reference
    CONSTRAINT FK_Image_Location FOREIGN KEY (location_id) REFERENCES Location(id)
);

-- 5 Associative table for Image-Person relationship (many-to-many)
CREATE TABLE Image_Person (
    Image_id INT,
    Person_id INT,
    PRIMARY KEY (Image_id, Person_id),
    FOREIGN KEY (Image_id) REFERENCES Image(id),
    FOREIGN KEY (Person_id) REFERENCES Person(id)
);

-- 6 Associative table for Image-Event relationship (many-to-many)
CREATE TABLE Image_Event (
    Image_id INT,
    Event_id INT,
    PRIMARY KEY (Image_id, Event_id),
    FOREIGN KEY (Image_id) REFERENCES Image(id),
    FOREIGN KEY (Event_id) REFERENCES Event(id)
);
