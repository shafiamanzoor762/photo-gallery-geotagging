-- Insert records into Location table
INSERT INTO Location (name, latitude, longitude) VALUES 
('Park', 40.712776, -74.005974),
('Museum', 34.052235, -118.243683),
('Library', 51.507351, -0.127758),
('Cafe', 48.856613, 2.352222);

-- Insert records into Person table
INSERT INTO Person (name, path, gender) VALUES
('Alina', '/images/alina.jpg', 'F'),
('Aliya', '/images/aliya.jpg', 'F'),
('Abeeha', '/images/abeeha.jpg', 'F'),
('Abeera', '/images/abeera.jpg', 'F');

-- Insert records into Event table
INSERT INTO Event (name) VALUES 
('Birthday Party'),
('Wedding'),
('Conference'),
('Picnic');

-- Insert records into Image table
INSERT INTO Image (path, is_sync, capture_date, event_date, last_modified, location_id) VALUES
('/images/event1.jpg', 1, '2023-12-01', '2023-12-02', '2023-12-03', 1),
('/images/event2.jpg', 0, '2023-11-01', '2023-11-05', '2023-11-06', 2),
('/images/event3.jpg', 1, '2023-10-01', '2023-10-10', '2023-10-11', 3),
('/images/event4.jpg', 0, '2023-09-01', '2023-09-15', '2023-09-16', 4);

-- Insert records into ImagePerson table (many-to-many relationship between Image and Person)
INSERT INTO ImagePerson (image_id, person_id) VALUES
(1, 1),  -- Alina linked to image 1
(1, 2),  -- Aliya linked to image 1
(2, 3),  -- Abeeha linked to image 2
(3, 4);  -- Abeera linked to image 3

-- Insert records into ImageEvent table (many-to-many relationship between Image and Event)
INSERT INTO ImageEvent (image_id, event_id) VALUES
(1, 1),  -- Image 1 linked to Birthday Party
(2, 2),  -- Image 2 linked to Wedding
(3, 3),  -- Image 3 linked to Conference
(4, 4);  -- Image 4 linked to Picnic

-- Insert records into Link table (relationships between persons)
INSERT INTO Link (person1_id, person2_id) VALUES
(1, 2),  -- Alina and Aliya are linked
(1, 3),  -- Alina and Abeeha are linked
(2, 4),  -- Aliya and Abeera are linked
(3, 4);  -- Abeeha and Abeera are linked
