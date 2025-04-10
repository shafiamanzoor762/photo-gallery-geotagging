-----imagehistory

CREATE TRIGGER trg_UpdateImageHistory_new
ON Image
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no,is_deleted,hash,is_active)
    SELECT 
        i.id,
        i.path,
        i.is_sync,
        i.capture_date,
        i.event_date,
        i.last_modified,
        i.location_id,
        ISNULL(MAX(h.version_no), 0) + 1,
		
		i.is_deleted,
		i.hash,
		0 as inactive
    FROM 
        Inserted i
    LEFT JOIN 
        ImageHistory h ON i.id = h.id
    GROUP BY 
        i.id, i.path, i.is_sync, i.capture_date, i.event_date, i.last_modified, i.location_id,i.is_deleted,i.hash;
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
        i.id,
		i.name,
        i.path,
		i.gender,
        
        ISNULL(MAX(h.version_no), 0) + 1
		
		
    FROM 
        Inserted i
    LEFT JOIN 
        PersonHistory h ON i.id = h.id
    GROUP BY 
        i.id,i.name, i.path,i.gender;
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
    INSERT INTO LinkHistroy (person1_id, person2_id, version_no,is_Active)
    SELECT 
        d.person1_id,
        d.person2_id,
        ISNULL(v.MaxVersion, 0) + 1 , -- Increment the version number
		0 AS is_active
    FROM 
        Deleted d  -- The 'Deleted' table holds the old data
    OUTER APPLY (
        SELECT MAX(version_no) AS MaxVersion
        FROM LinkHistory
        WHERE person1_id = d.person1_id AND person2_id = d.person2_id
    ) v;
END;

