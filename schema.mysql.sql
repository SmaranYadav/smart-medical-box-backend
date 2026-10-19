CREATE TABLE IF NOT EXISTS user_login_details (
    user_id INT NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    mobile_number VARCHAR(32) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_medicine_track_details (
    medicine_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency SMALLINT NOT NULL CHECK (frequency BETWEEN 1 AND 4),
    dose_times JSON NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    instructions TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active', 'Completed', 'Deleted')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (medicine_id),
    INDEX ix_medicine_user_status_created (user_id, status, created_at),
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
    INDEX ix_push_subscriptions_user (user_id),
    CONSTRAINT fk_push_subscription_user
        FOREIGN KEY (user_id) REFERENCES user_login_details (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS medicine_reminder_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    medicine_id INT NOT NULL,
    dose_date DATE NOT NULL,
    dose_time VARCHAR(5) NOT NULL,
    endpoint_hash CHAR(64) NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_medicine_reminder_dose_endpoint (
        medicine_id, dose_date, dose_time, endpoint_hash
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
