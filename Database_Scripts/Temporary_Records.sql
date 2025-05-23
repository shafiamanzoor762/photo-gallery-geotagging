-- Insert records into Location table
INSERT INTO Location (name, latitude, longitude) VALUES 
('BIIT', 33.6432715788722, 73.07902684454514),
('Sports Ground', 33.643285534790735, 73.07859433834076),
('Library', 33.643240875842814, 73.07872777823846),
('BIIT Amphitheatre', 33.643343591388884, 73.07889943961703);

-- Insert records into Person table
INSERT INTO Person (name, path, gender) VALUES
('Sir Noman', '/face_images/ba5a33aca3bb475f89dc7e57d24432a6.jpg', 'F'),
('Sir Ahsan', '/images/f8d03d6f37174faf803a7a21c3338842.jpg', 'F'),
('Abeeha', '/images/abeeha.jpg', 'F'),
('Abeera', '/images/abeera.jpg', 'F');

-- Insert records into Event table
INSERT INTO Event (name) VALUES 
('Birthday Party'),
('Wedding'),
('Conference'),
('Picnic');


INSERT INTO Image (path, is_sync, capture_date, event_date, last_modified, location_id) VALUES
('/images/event1.jpg', 0, '2023-12-01', null, '2023-12-03', null)
 
-- Insert records into Image table
INSERT INTO Image (path, is_sync, capture_date, event_date, last_modified, location_id) VALUES
('/images/Snapinsta.app_467019764_1046914550780505_5493082528341713749_n_1080.jpg', 1, '2023-12-01', '2023-12-02', '2023-12-03', 1),
('/images/Snapinsta.app_467148011_1046914534113840_6542700807049905997_n_1080.jpg', 0, '2023-11-01', '2023-11-05', '2023-11-06', 2),
('/images/event3.jpg', 1, '2023-10-01', '2023-10-10', '2023-10-11', 3),
('/images/event4.jpg', 0, '2023-09-01', '2023-09-15', '2023-09-16', 4);

-- Insert records into ImagePerson table (many-to-many relationship between Image and Person)
INSERT INTO ImagePerson (image_id, person_id) VALUES
(1, 1),  --Sir Noman  linked to image 1
(1, 2),  -- Aliya linked to image 1
(2, 3),  -- Abeeha linked to image 2
(3, 4);  -- Abeera linked to image 3

-- Insert records into ImageEvent table (many-to-many relationship between Image and Event)
INSERT INTO ImageEvent (image_id, event_id) VALUES
(1003, 1),  -- Image 1 linked to Birthday Party
(2, 2),  -- Image 2 linked to Wedding
(3, 3),  -- Image 3 linked to Conference
(4, 4);  -- Image 4 linked to Picnic

-- Insert records into Link table (relationships between persons)
INSERT INTO Link (person1_id, person2_id) VALUES
(1, 2),  -- Alina and Aliya are linked
(1, 3),  -- Alina and Abeeha are linked
(2, 4),  -- Aliya and Abeera are linked
(3, 4);  -- Abeeha and Abeera are linked




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
