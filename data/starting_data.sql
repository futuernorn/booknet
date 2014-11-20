-- pass: R13dVs2ugr92
-- print bcrypt.hashpw('R13dVs2ugr92', bcrypt.gensalt())
-- $2a$12$zSGiaiyHbCja0hsc4fBO9OCqENjF.zb0CdarlkuY1tDGUDfp56QE2

INSERT INTO user_level (level_name, level_description)
    VALUES('Administrator', 'Administrator');

INSERT INTO "user" (login_name, email, password, level_id, date_created, is_active)
VALUES('norn', 'js1921@txstate.edu', '$2a$12$zSGiaiyHbCja0hsc4fBO9OCqENjF.zb0CdarlkuY1tDGUDfp56QE2', 1, current_timestamp, true);
