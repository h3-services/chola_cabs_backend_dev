# Deploy Driver Live Location

## 1. Pull Latest Code
```bash
cd /root/cab_app
git pull origin main
```

## 2. Update Database
Run the following SQL in your MySQL database to create the new table:
```sql
CREATE TABLE driver_live_location (
  driver_id CHAR(36) PRIMARY KEY,
  latitude DECIMAL(10,8) NOT NULL,
  longitude DECIMAL(11,8) NOT NULL,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_driver_location_driver FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
);
```

## 3. Verify Dependencies (Optional)
No new python packages were added, but good to check:
```bash
pip install -r requirements.txt
```

## 4. Restart Service
```bash
systemctl restart cab-api
systemctl status cab-api
```

## 5. Verify Feature
You can test the new endpoints:
```bash
# Update location
curl -X POST "http://localhost:8000/drivers/<YOUR_DRIVER_ID>/location" -H "Content-Type: application/json" -d '{"latitude": 12.9716, "longitude": 77.5946}'

# Get location
curl "http://localhost:8000/drivers/<YOUR_DRIVER_ID>/location"
```
