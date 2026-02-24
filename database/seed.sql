-- Seed Data for SERVICED

-- 1. Insert Users
-- Admin
INSERT INTO users (full_name, email, password_hash, role, phone, location, avatar_initials) VALUES
('Super Admin', 'admin@serviced.com', 'hashed_secret_123', 'admin', '+1000000000', 'Cloud', 'AD');

-- Providers
INSERT INTO users (full_name, email, password_hash, role, phone, location, avatar_initials) VALUES
('Ana María', 'ana.maria@provider.com', 'hashed_secret_123', 'provider', '+34 600 999 888', 'Madrid, ES', 'AM'),
('Juan Técnico', 'juan.tech@provider.com', 'hashed_secret_123', 'provider', '+34 600 777 666', 'Barcelona, ES', 'JT');

-- Clients
INSERT INTO users (full_name, email, password_hash, role, phone, location, avatar_initials) VALUES
('Alejandro López', 'alejandro.l@email.com', 'hashed_secret_123', 'client', '+34 600 123 456', 'Madrid, España', 'AL'),
('Sofía Martínez', 'sofia.m@email.com', 'hashed_secret_123', 'client', '+34 600 111 222', 'Valencia, ES', 'SM'),
('Hospital Privado Central', 'contacto@hospital.com', 'hashed_secret_123', 'client', '+34 911 222 333', 'Madrid, ES', 'HP'),
('Tech Solutions S.L.', 'admin@techsolutions.com', 'hashed_secret_123', 'client', '+34 933 444 555', 'Barcelona, ES', 'TS');


-- 2. Insert Services
-- Ana María's Services
INSERT INTO services (provider_id, title, description, category, price, price_unit, is_active) VALUES
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 'Limpieza de Oficinas', 'Servicio profesional de limpieza para oficinas y locales comerciales. Incluye materiales.', 'home', 45.00, 'hour', TRUE),
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 'Organización de Espacios', 'Organización profesional de armarios, almacenes y garajes.', 'home', 30.00, 'hour', TRUE),
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 'Limpieza Post-Obra', 'Limpieza profunda después de reformas o construcciones.', 'home', 65.00, 'hour', FALSE); -- Pausado

-- Juan's Services
INSERT INTO services (provider_id, title, description, category, price, price_unit, is_active) VALUES
((SELECT user_id FROM users WHERE email = 'juan.tech@provider.com'), 'Reparación de Aire Acondicionado', 'Mantenimiento y reparación de unidades split y centralizadas.', 'repairs', 80.00, 'fixed', TRUE);


-- 3. Insert Service Requests
-- Request: Hospital -> Limpieza de Oficinas (NEW)
INSERT INTO service_requests (client_id, service_id, status, initial_message, request_date) VALUES
(
    (SELECT user_id FROM users WHERE email = 'contacto@hospital.com'),
    (SELECT service_id FROM services WHERE title = 'Limpieza de Oficinas'),
    'new',
    'Necesitamos limpieza urgente para el ala oeste.',
    NOW() - INTERVAL '30 minutes'
);

-- Request: Sofía -> Organización (NEW)
INSERT INTO service_requests (client_id, service_id, status, initial_message, request_date) VALUES
(
    (SELECT user_id FROM users WHERE email = 'sofia.m@email.com'),
    (SELECT service_id FROM services WHERE title = 'Organización de Espacios'),
    'new',
    'Tengo un trastero muy desordenado.',
    NOW() - INTERVAL '2 hours'
);

-- Request: Tech Solutions -> Limpieza Post-Obra (PENDING)
INSERT INTO service_requests (client_id, service_id, status, initial_message, request_date) VALUES
(
    (SELECT user_id FROM users WHERE email = 'admin@techsolutions.com'),
    (SELECT service_id FROM services WHERE title = 'Limpieza Post-Obra'),
    'pending',
    'Acabamos de pintar la oficina central.',
    NOW() - INTERVAL '1 day'
);

-- Request: Alejandro -> Limpieza de Oficinas (COMPLETED - for Review testing)
INSERT INTO service_requests (client_id, service_id, status, initial_message, request_date) VALUES
(
    (SELECT user_id FROM users WHERE email = 'alejandro.l@email.com'),
    (SELECT service_id FROM services WHERE title = 'Limpieza de Oficinas'),
    'completed',
    'Servicio recurrente semanal por favor.',
    NOW() - INTERVAL '5 days'
);

-- 4. Insert Reviews
INSERT INTO reviews (request_id, rating, comment) VALUES
(
    (SELECT request_id FROM service_requests WHERE status = 'completed' LIMIT 1),
    5,
    '¡Excelente servicio! Ana María es muy profesional y detallista.'
);

-- 5. Insert Messages
INSERT INTO messages (sender_id, receiver_id, request_id, message_text, is_read, created_at) VALUES
(
    (SELECT user_id FROM users WHERE email = 'alejandro.l@email.com'),
    (SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'),
    (SELECT request_id FROM service_requests WHERE status = 'completed' LIMIT 1),
    '¿Podrías venir un poco antes la próxima vez?',
    TRUE,
    NOW() - INTERVAL '4 days'
),
(
    (SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'),
    (SELECT user_id FROM users WHERE email = 'alejandro.l@email.com'),
    (SELECT request_id FROM service_requests WHERE status = 'completed' LIMIT 1),
    'Claro Alejandro, sin problema. A las 9:00 está bien?',
    FALSE,
    NOW() - INTERVAL '4 days'
);

-- 6. Insert Payments
INSERT INTO payments (request_id, amount, status, payment_method, transaction_id) VALUES
(
    (SELECT request_id FROM service_requests WHERE status = 'completed' LIMIT 1),
    45.00,
    'completed',
    'credit_card',
    'txn_123456789'
);

-- 7. Insert Favorites
INSERT INTO favorites (client_id, service_id) VALUES
(
    (SELECT user_id FROM users WHERE email = 'sofia.m@email.com'),
    (SELECT service_id FROM services WHERE title = 'Reparación de Aire Acondicionado')
);

-- 8. Insert Availability (Ana María: Mon-Fri 9-5)
INSERT INTO provider_availability (provider_id, day_of_week, start_time, end_time) VALUES
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 1, '09:00', '17:00'), -- Mon
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 2, '09:00', '17:00'), -- Tue
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 3, '09:00', '17:00'), -- Wed
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 4, '09:00', '17:00'), -- Thu
((SELECT user_id FROM users WHERE email = 'ana.maria@provider.com'), 5, '09:00', '14:00'); -- Fri (Early finish)
