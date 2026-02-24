-- Schema for SERVICED
-- Inferred from seed.sql and project requirements

DROP TABLE IF EXISTS provider_availability CASCADE;
DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS service_requests CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'provider', 'client')),
    phone VARCHAR(50),
    location VARCHAR(255),
    avatar_initials VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Services
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    price_unit VARCHAR(50) NOT NULL, -- 'hour', 'fixed'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Service Requests
CREATE TABLE service_requests (
    request_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'new', -- 'new', 'pending', 'accepted', 'completed', 'cancelled'
    initial_message TEXT,
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Reviews
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES service_requests(request_id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Messages
CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    request_id INTEGER REFERENCES service_requests(request_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Payments
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES service_requests(request_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'pending', 'completed', 'failed'
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Favorites
CREATE TABLE favorites (
    favorite_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(service_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, service_id)
);

-- 8. Provider Availability
CREATE TABLE provider_availability (
    availability_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sun, 1=Mon...
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    UNIQUE(provider_id, day_of_week)
);
