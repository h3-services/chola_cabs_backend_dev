
-- ⚠️ RUN THESE COMMANDS IN YOUR MYSQL WORKBENCH ⚠️
-- Use the database that your app is connected to
USE cab_app;

-- Add the missing columns manually
ALTER TABLE trips 
ADD COLUMN waiting_charges DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN inter_state_permit_charges DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN driver_allowance DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN luggage_cost DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN pet_cost DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN toll_charges DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN night_allowance DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00;

-- Verify they are added
DESCRIBE trips;
