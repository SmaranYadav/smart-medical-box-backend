CREATE TABLE IF NOT EXISTS user_login_details (
    user_id INT NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    mobile_number VARCHAR(32) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_login_details_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_medicine_track_details (
    medicine_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency TINYINT UNSIGNED NOT NULL,
    dose_times JSON NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    instructions TEXT NOT NULL,
    status ENUM('Active', 'Completed', 'Deleted') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (medicine_id),
    KEY ix_medicine_user_status_created (user_id, status, created_at),
    CONSTRAINT fk_medicine_user
        FOREIGN KEY (user_id) REFERENCES user_login_details (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS push_subscriptions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh VARCHAR(255) NOT NULL,
    auth VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    KEY ix_push_subscriptions_user (user_id),
    CONSTRAINT fk_push_subscription_user
        FOREIGN KEY (user_id) REFERENCES user_login_details (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
