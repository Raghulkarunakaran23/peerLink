-- Create the database
CREATE DATABASE IF NOT EXISTS peerlink_db;

-- Use the database
USE peerlink_db;

-- Table for user authentication and profile
CREATE TABLE student_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bio TEXT,
    mobile VARCHAR(15) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Table for events
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT
);

-- Table for user-event relationships (RSVPs)
CREATE TABLE user_event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Table for circles
CREATE TABLE circles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255)
);

-- Table for user-circle relationships
CREATE TABLE user_circle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    circle_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE,
    FOREIGN KEY (circle_id) REFERENCES circles(id) ON DELETE CASCADE
);

-- Table for posts in the social feed
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    badge VARCHAR(10),
    image_url VARCHAR(255),
    user_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);

-- Table for XP tracking
CREATE TABLE user_xp (
    user_id INT PRIMARY KEY,
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    title VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);

-- Table for milestones
CREATE TABLE milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    unlocked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);

-- Table for rewards
CREATE TABLE rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    xp_cost INT NOT NULL
);

-- Table for XP history
CREATE TABLE xp_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    amount INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);

-- Table for user bio
CREATE TABLE user_bio (
    user_id INT PRIMARY KEY,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE
);

-- Table for user rewards
CREATE TABLE user_rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reward_id INT NOT NULL,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES student_login(id) ON DELETE CASCADE,
    FOREIGN KEY (reward_id) REFERENCES rewards(id) ON DELETE CASCADE
);