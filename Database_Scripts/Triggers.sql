-----imagehistory

drop trigger trg_UpdateImageHistory_new

CREATE TRIGGER trg_UpdateImageHistory_new
ON Image
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no,is_deleted,hash,is_active)
    SELECT 
        d.id,
        d.path,
        d.is_sync,
        d.capture_date,
        d.event_date,
        d.last_modified,
        d.location_id,
        ISNULL(MAX(h.version_no), 0) + 1,
		
		d.is_deleted,
		d.hash,
		0 as inactive
    FROM 
        Deleted d
    LEFT JOIN 
        ImageHistory h ON d.id = h.id
    GROUP BY 
        d.id, d.path, d.is_sync, d.capture_date, d.event_date, d.last_modified, d.location_id,d.is_deleted,d.hash;
END;



-----personHistory

CREATE TRIGGER trg_UpdatePerosnHistory_new
ON Person
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO PersonHistory (id, name,path,gender,version_no)
    SELECT 
        d.id,
		d.name,
        d.path,
		d.gender,
        
        ISNULL(MAX(h.version_no), 0) + 1
		
		
    FROM 
        Deleted d
    LEFT JOIN 
        PersonHistory h ON d.id = h.id
    GROUP BY 
        d.id,d.name, d.path,d.gender;
END;


-----------ImageEventhistory
CREATE TRIGGER trg_UpdateImageEventHistory
ON ImageEvent
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Insert the old data (before update) into the history table
    INSERT INTO ImageEventHistory (image_id, event_id, version_no,is_Active)
    SELECT 
        d.image_id,
        d.event_id,
        ISNULL(v.MaxVersion, 0) + 1 , -- Increment the version number
		0 AS is_active
    FROM 
        Deleted d  -- The 'Deleted' table holds the old data
    OUTER APPLY (
        SELECT MAX(version_no) AS MaxVersion
        FROM ImageEventHistory
        WHERE image_id = d.image_id AND event_id = d.event_id
    ) v;
END;

------------------Imageperson
CREATE TRIGGER trg_UpdateImagePersonHistory
ON ImagePerson
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Insert the old data (before update) into the history table
    INSERT INTO ImagePersonHistory (image_id, person_id, version_no,is_Active)
    SELECT 
        d.image_id,
        d.person_id,
        ISNULL(v.MaxVersion, 0) + 1 , -- Increment the version number
		0 AS is_active
    FROM 
        Deleted d  -- The 'Deleted' table holds the old data
    OUTER APPLY (
        SELECT MAX(version_no) AS MaxVersion
        FROM ImagepersonHistory
        WHERE image_id = d.image_id AND person_id = d.person_id
    ) v;
END;


---------------linkperson
CREATE TRIGGER trg_UpdateLinkHistory
ON Link
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Insert the old data (before update) into the history table
    INSERT INTO LinkHistory (person1_id, person2_id, version_no, is_Active)
    SELECT 
        d.person1_id,
        d.person2_id,
        ISNULL(v.MaxVersion, 0) + 1,  -- Increment the version number based on the maximum version
        0 AS is_active
    FROM 
        Deleted d  -- The 'Deleted' table holds the old data (before update)
    OUTER APPLY (
        SELECT MAX(version_no) AS MaxVersion
        FROM LinkHistory
        WHERE person1_id = d.person1_id AND person2_id = d.person2_id
    ) v;
END;



-----create column is_active in each histry table for example
ALTER TABLE LinkHistory
ADD is_active BIT;

ALTER TABLE ImageHistory
ADD is_active varchar(64) NOT NULL;