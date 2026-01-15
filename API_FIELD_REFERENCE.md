# Complete API Field Reference

## Overview
All GET API endpoints now return complete field sets from database tables with no missing fields.

## Drivers Endpoint
**GET** `/api/v1/drivers/` and `/api/v1/drivers/{driver_id}`

**Fields Returned (19 total)**:
1. `driver_id` - Unique driver identifier (UUID)
2. `name` - Driver's full name
3. `phone_number` - Contact phone number
4. `email` - Email address
5. `kyc_verified` - KYC verification status (boolean)
6. `primary_location` - Primary operating location
7. `photo_url` - Driver profile photo URL
8. `aadhar_url` - Aadhar document URL
9. `licence_url` - License document URL
10. `licence_number` - License number
11. `aadhar_number` - Aadhar number
12. `licence_expiry` - License expiry date (ISO format)
13. `wallet_balance` - Current wallet balance (decimal)
14. `device_id` - Mobile device identifier
15. `is_available` - Availability status (boolean)
16. `is_approved` - Approval status (boolean)
17. `errors` - Error messages/validation issues
18. `created_at` - Creation timestamp (ISO format)
19. `updated_at` - Last update timestamp (ISO format)

---

## Vehicles Endpoint
**GET** `/api/v1/vehicles/`, `/api/v1/vehicles/{vehicle_id}`, `/api/v1/vehicles/driver/{driver_id}`

**Fields Returned (20 total)**:
1. `vehicle_id` - Unique vehicle identifier
2. `driver_id` - Associated driver ID
3. `vehicle_type` - Type of vehicle
4. `vehicle_brand` - Vehicle manufacturer
5. `vehicle_model` - Vehicle model
6. `vehicle_number` - Registration number
7. `vehicle_color` - Vehicle color
8. `seating_capacity` - Number of seats
9. `rc_expiry_date` - RC expiry date (ISO format)
10. `fc_expiry_date` - FC expiry date (ISO format)
11. `vehicle_approved` - Approval status (boolean)
12. `rc_book_url` - RC document URL
13. `fc_certificate_url` - FC document URL
14. `vehicle_front_url` - Front photo URL
15. `vehicle_back_url` - Back photo URL
16. `vehicle_left_url` - Left side photo URL
17. `vehicle_right_url` - Right side photo URL
18. `errors` - Error messages/validation issues
19. `created_at` - Creation timestamp (ISO format)
20. `updated_at` - Last update timestamp (ISO format)

---

## Trips Endpoint
**GET** `/api/v1/trips/`, `/api/v1/trips/{trip_id}`, `/api/v1/trips/driver/{driver_id}`

**Fields Returned (22 total)**:
1. `trip_id` - Unique trip identifier
2. `customer_name` - Customer's name
3. `customer_phone` - Customer's phone number
4. `pickup_address` - Pickup location
5. `drop_address` - Drop-off location
6. `trip_type` - Type (one_way, round_trip)
7. `vehicle_type` - Required vehicle type
8. `assigned_driver_id` - Assigned driver ID
9. `trip_status` - Current status (pending, assigned, started, completed, cancelled)
10. `distance_km` - Trip distance in kilometers
11. `odo_start` - Starting odometer reading
12. `odo_end` - Ending odometer reading
13. `fare` - Trip fare amount (decimal)
14. `started_at` - Trip start time (ISO format)
15. `ended_at` - Trip end time (ISO format)
16. `planned_start_at` - Planned start time (ISO format)
17. `planned_end_at` - Planned end time (ISO format)
18. `is_manual_assignment` - Manual assignment flag (boolean)
19. `passenger_count` - Number of passengers
20. `errors` - Error messages/validation issues
21. `created_at` - Creation timestamp (ISO format)
22. `updated_at` - Last update timestamp (ISO format)

---

## Date/Time Format
All date and datetime fields are returned in ISO 8601 format:
- **Date**: `YYYY-MM-DD` (e.g., "2026-01-15")
- **DateTime**: `YYYY-MM-DDTHH:MM:SS` (e.g., "2026-01-15T22:49:22")

## Null Values
Fields that are optional or not yet populated will return `null` in JSON responses.
