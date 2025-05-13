CREATE TABLE IF NOT EXISTS user_bio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);
