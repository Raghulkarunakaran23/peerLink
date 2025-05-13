ALTER TABLE student_login
ADD COLUMN name VARCHAR(100) NOT NULL AFTER id,
ADD COLUMN bio TEXT AFTER name,
ADD COLUMN mobile VARCHAR(15) NOT NULL AFTER bio;

-- Add a new table for user bios
CREATE TABLE IF NOT EXISTS user_bio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);
