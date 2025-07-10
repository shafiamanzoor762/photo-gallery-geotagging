-----imagehistory
------new trigger ------
ALTER TRIGGER trg_UpdateImageHistory_new
ON Image
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no, is_deleted, hash, is_active, created_at)
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
        0 as is_active,
        SYSDATETIME() AS created_at
    FROM
        Deleted d
    INNER JOIN
        Inserted i ON d.id = i.id
    LEFT JOIN
        ImageHistory h ON d.id = h.id
    WHERE
        -- Only check for changes in these specific "core" columns
        (d.path IS NULL AND i.path IS NOT NULL) OR (d.path IS NOT NULL AND i.path IS NULL) OR (d.path <> i.path) OR
        (d.location_id IS NULL AND i.location_id IS NOT NULL) OR (d.location_id IS NOT NULL AND i.location_id IS NULL) OR (d.location_id <> i.location_id) OR
        (d.is_deleted <> i.is_deleted) OR
        (d.hash IS NULL AND i.hash IS NOT NULL) OR (d.hash IS NOT NULL AND i.hash IS NULL) OR (d.hash <> i.hash)
        -- Removed: is_sync, capture_date, event_date from the change detection condition
    GROUP BY
        d.id, d.path, d.is_sync, d.capture_date, d.event_date, d.last_modified, d.location_id, d.is_deleted, d.hash;
END;




--------------------------------------
drop trigger trg_UpdateImageHistory_new

CREATE TRIGGER trg_UpdateImageHistory_new
ON Image
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no,is_deleted,hash,is_active,created_at)
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
		0 as is_active,
        SYSDATETIME() AS created_at
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

    INSERT INTO PersonHistory (id, name,path,gender,version_no,is_Active,created_at,DOB,Age)
    SELECT 
        d.id,
		d.name,
        d.path,
		d.gender,
        
        ISNULL(MAX(h.version_no), 0) + 1,
		0,
        SYSDATETIME() AS created_at,
        d.DOB,
        d.Age
		
    FROM 
        Deleted d
    LEFT JOIN 
        PersonHistory h ON d.id = h.id
    GROUP BY 
        d.id,d.name, d.path,d.gender,d.DOB,d.Age;
END;


-----------ImageEventhistory
CREATE TRIGGER trg_UpdateImageEventHistory
ON ImageEvent
AFTER Delete
AS
BEGIN
    SET NOCOUNT ON;

    -- Insert the old data (before update) into the history table
    INSERT INTO ImageEventHistory (image_id, event_id, version_no,is_Active,created_at)
    SELECT 
        d.image_id,
        d.event_id,
        ISNULL(v.MaxVersion, 0) + 1 , -- Increment the version number
		0 AS is_active,
        SYSDATETIME() AS created_at
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









-- ======================================

CREATE TRIGGER trg_UpdateImageHistory_new
ON Image
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageHistory (
        id, path, is_sync, capture_date, event_date, last_modified,
        location_id, version_no, is_deleted, is_active, hash, created_at
    )
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
        0 AS is_active,  -- ✅ set inactive for undo purpose
        d.hash,
        SYSDATETIME()
    FROM
        Deleted d
    INNER JOIN
        Inserted i ON d.id = i.id
    LEFT JOIN
        ImageHistory h ON h.id = d.id
    WHERE
           (ISNULL(d.path, '') <> ISNULL(i.path, '')) 
    -- (ISNULL(d.location_id, -1) <> ISNULL(i.location_id, -1)) OR
    -- (ISNULL(d.is_deleted, 0) <> ISNULL(i.is_deleted, 0)) OR
    -- (ISNULL(d.hash, '') <> ISNULL(i.hash, '')) OR
    -- -- (ISNULL(d.last_modified, '1900-01-01') <> ISNULL(i.last_modified, '1900-01-01')) OR
    -- (ISNULL(d.is_sync, 1) <> ISNULL(i.is_sync, 1))
        
    GROUP BY
        d.id, d.path, d.is_sync, d.capture_date, d.event_date,
        d.last_modified, d.location_id, d.is_deleted, d.hash;
END;




CREATE TRIGGER trg_Delete_ImageEventHistory
ON ImageEvent
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO ImageEventHistory (
        image_id,
        event_id,
        version_no,
        is_active,
        created_at
    )
    SELECT
        d.image_id,
        d.event_id,
        ISNULL(MAX(h.version_no), 0) + 1,
        '0',
        SYSDATETIME()
    FROM Deleted d
    LEFT JOIN ImageEventHistory h
        ON h.image_id = d.image_id AND h.event_id = d.event_id
    GROUP BY d.image_id, d.event_id;
END;



CREATE TRIGGER trg_UpdatePersonHistory
ON Person
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO PersonHistory (
        id, name, path, gender, DOB, Age,
        version_no, is_active, created_at
    )
    SELECT
        d.id,
        d.name,
        d.path,
        d.gender,
        d.DOB,
        d.Age,
        ISNULL(MAX(ph.version_no), 0) + 1,
        '0',
        SYSDATETIME()
    FROM Deleted d
    INNER JOIN Inserted i ON d.id = i.id
    LEFT JOIN PersonHistory ph ON ph.id = d.id
    WHERE 
        (ISNULL(d.name, '') <> ISNULL(i.name, '')) OR
        (ISNULL(d.path, '') <> ISNULL(i.path, '')) OR
        (ISNULL(d.gender, '') <> ISNULL(i.gender, '')) OR
        (ISNULL(d.DOB, '1900-01-01') <> ISNULL(i.DOB, '1900-01-01')) OR
        (ISNULL(d.Age, -1) <> ISNULL(i.Age, -1))
    GROUP BY 
        d.id, d.name, d.path, d.gender, d.DOB, d.Age;
END;

-- ====================   akhri 


-- CREATE TRIGGER trg_UpdateImageEventHistory
-- ON ImageEvent
-- AFTER Delete
-- AS
-- BEGIN
--     SET NOCOUNT ON;

--     -- Insert the old data (before update) into the history table
--     INSERT INTO ImageEventHistory (image_id, event_id, version_no,is_Active,created_at)
--     SELECT 
--         d.image_id,
--         d.event_id,
--         ISNULL(v.MaxVersion, 0) + 1 , -- Increment the version number
-- 		0 AS is_active,
--         SYSDATETIME() AS created_at
--     FROM 
--         Deleted d  -- The 'Deleted' table holds the old data
--     OUTER APPLY (
--         SELECT MAX(version_no) AS MaxVersion
--         FROM ImageEventHistory
--         WHERE image_id = d.image_id AND event_id = d.event_id
--     ) v;
-- END;

-- CREATE TRIGGER trg_UpdatePersonHistory
-- ON Person
-- AFTER UPDATE
-- AS
-- BEGIN
--     SET NOCOUNT ON;

--     INSERT INTO PersonHistory (
--         id, name, path, gender, DOB, Age,
--         version_no, is_active, created_at
--     )
--     SELECT
--         d.id,
--         d.name,
--         d.path,
--         d.gender,
--         d.DOB,
--         d.Age,
--         ISNULL(MAX(ph.version_no), 0) + 1,
--         '0',
--         SYSDATETIME()
--     FROM Deleted d
--     INNER JOIN Inserted i ON d.id = i.id
--     LEFT JOIN PersonHistory ph ON ph.id = d.id
--     WHERE 
--         (ISNULL(d.name, '') <> ISNULL(i.name, '')) OR
--         (ISNULL(d.path, '') <> ISNULL(i.path, '')) OR
--         (ISNULL(d.gender, '') <> ISNULL(i.gender, '')) OR
--         (ISNULL(d.DOB, '1900-01-01') <> ISNULL(i.DOB, '1900-01-01')) OR
--         (ISNULL(d.Age, -1) <> ISNULL(i.Age, -1))
--     GROUP BY 
--         d.id, d.name, d.path, d.gender, d.DOB, d.Age;
-- END;



-- create TRIGGER trg_UpdateImageHistory
-- ON Image
-- AFTER UPDATE
-- AS
-- BEGIN
--     SET NOCOUNT ON;

--     INSERT INTO ImageHistory (id, path, is_sync, capture_date, event_date, last_modified, location_id, version_no, is_deleted, hash, is_active, created_at)
--     SELECT
--         d.id,
--         d.path,
--         d.is_sync,
--         d.capture_date,
--         d.event_date,
--         d.last_modified,
--         d.location_id,
--         ISNULL(MAX(h.version_no), 0) + 1,
--         d.is_deleted,
--         d.hash,
--         0 as is_active,
--         SYSDATETIME() AS created_at
--     FROM
--         Deleted d
--     INNER JOIN
--         Inserted i ON d.id = i.id
--     LEFT JOIN
--         ImageHistory h ON d.id = h.id
    
--     GROUP BY
--         d.id, d.path, d.is_sync, d.capture_date, d.event_date, d.last_modified, d.location_id, d.is_deleted, d.hash;
-- END;
