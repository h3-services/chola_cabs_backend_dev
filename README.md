# 🚗 Cab Booking Management API

Production-ready FastAPI backend for comprehensive cab booking system with MySQL database.

## 🚀 Features

- **Driver Management** - CRUD operations, availability tracking, wallet management
- **Vehicle Management** - Vehicle registration, approval system
- **Trip Management** - Trip creation, driver assignment, status tracking
- **Tariff System** - Dynamic pricing based on vehicle type and trip type
- **Real-time Status** - Driver availability, trip status updates
- **Production Ready** - Environment-based config, error handling, logging

## 🛠 Tech Stack

- **Backend**: Python 3.8+ with FastAPI
- **Database**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+ database
- pip package manager

## ⚡ Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/PraveenCoder2007/cab_app.git
cd cab_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Run Application
```bash
python app/main.py
# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Stats**: http://localhost:8000/api/v1/stats

## 🗄️ Database Schema

The system uses your existing MySQL database with these tables:
- `drivers` - Driver profiles and status
- `vehicles` - Vehicle information and approval
- `trips` - Trip records and tracking
- `trip_driver_requests` - Driver-trip assignment requests
- `payment_transactions` - Payment records
- `wallet_transactions` - Wallet transaction history
- `vehicle_tariff_config` - Pricing configuration
- `error_handling` - Error logging

## 📚 API Documentation

Detailed API documentation is available in the `docs/api/` directory:

### Core APIs
- **[Drivers API](docs/api/drivers.md)** - Complete driver management, registration, availability, and wallet operations
- **[Vehicles API](docs/api/vehicles.md)** - Vehicle registration, approval workflow, and driver-vehicle associations
- **[Trips API](docs/api/trips.md)** - Trip lifecycle management, driver assignment, and status tracking
- **[Payments API](docs/api/payments.md)** - Payment transaction management and gateway integration
- **[Wallet Transactions API](docs/api/wallet_transactions.md)** - Driver wallet credits, debits, and balance management

### Configuration & Admin APIs
- **[Tariff Configuration API](docs/api/tariff_config.md)** - Dynamic pricing and fare calculation management
- **[Raw Data API](docs/api/raw_data.md)** - Direct database access for administrative tasks

### 📋 Quick API Reference

#### 👨💼 Driver Management
```
GET    /api/v1/drivers              # Get all drivers
GET    /api/v1/drivers/{id}         # Get driver by ID
POST   /api/v1/drivers              # Create new driver
PUT    /api/v1/drivers/{id}         # Update driver
PATCH  /api/v1/drivers/{id}/availability  # Update availability
GET    /api/v1/drivers/{id}/wallet-balance # Get wallet balance
```

#### 🚙 Vehicle Management
```
GET    /api/v1/vehicles             # Get all vehicles
GET    /api/v1/vehicles/{id}        # Get vehicle details
GET    /api/v1/vehicles/driver/{id} # Get vehicles by driver
POST   /api/v1/vehicles             # Add vehicle to driver
PUT    /api/v1/vehicles/{id}        # Update vehicle
PATCH  /api/v1/vehicles/{id}/approve # Approve vehicle
```

#### 🛣️ Trip Management
```
GET    /api/v1/trips                # Get all trips
GET    /api/v1/trips/{id}           # Get trip details
POST   /api/v1/trips                # Create new trip
PUT    /api/v1/trips/{id}           # Update trip
PATCH  /api/v1/trips/{id}/assign-driver/{driver_id} # Assign driver
PATCH  /api/v1/trips/{id}/status    # Update trip status
POST   /api/v1/trips/{id}/driver-requests # Create driver request
GET    /api/v1/trips/driver/{id}    # Get trips by driver
```

## 🧪 Testing with Postman

### 1. Import Collection
Create a new Postman collection with base URL: `http://localhost:8000`

### 2. Test Endpoints

**Create Driver:**
```json
POST /api/v1/drivers
{
  "name": "John Doe",
  "phone_number": "9876543210",
  "email": "john@example.com",
  "primary_location": "Mumbai",
  "licence_number": "MH123456789"
}
```

**Add Vehicle:**
```json
POST /api/v1/vehicles
{
  "driver_id": 1,
  "vehicle_type": "sedan",
  "vehicle_brand": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_number": "MH01AB1234",
  "vehicle_color": "White",
  "seating_capacity": 4
}
```

**Create Trip:**
```json
POST /api/v1/trips
{
  "customer_name": "Jane Smith",
  "customer_phone": "9876543211",
  "pickup_address": "Mumbai Airport",
  "drop_address": "Bandra West",
  "trip_type": "one_way",
  "vehicle_type": "sedan",
  "passenger_count": 2
}
```

## 🚀 Production Deployment on Linux VPS

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Install MySQL client
sudo apt install mysql-client -y
```

### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/PraveenCoder2007/cab_app.git
cd cab_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
# Edit .env with production values
nano .env
```

### 3. Create Systemd Service
```bash
sudo nano /etc/systemd/system/cab-api.service
```

Add this content:
```ini
[Unit]
Description=Cab Booking API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cab_app
Environment=PATH=/home/ubuntu/cab_app/venv/bin
ExecStart=/home/ubuntu/cab_app/venv/bin/python app/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 4. Start and Enable Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable cab-api

# Start the service
sudo systemctl start cab-api

# Check status
sudo systemctl status cab-api

# View logs
sudo journalctl -u cab-api -f
```

### 5. Nginx Configuration (Optional)
```bash
sudo nano /etc/nginx/sites-available/cab-api
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/cab-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Environment Variables

Create `.env` file with these variables:
```env
# Database Configuration
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

# Application Configuration
APP_NAME=Cab Booking API
APP_VERSION=1.0.0
DEBUG=False

# Security
SECRET_KEY=your_production_secret_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## 📊 Monitoring and Logs

### Check Service Status
```bash
sudo systemctl status cab-api
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u cab-api -f

# Last 100 lines
sudo journalctl -u cab-api -n 100
```

### Restart Service
```bash
sudo systemctl restart cab-api
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` template
2. **Use strong passwords** - For database and secret keys
3. **Configure CORS properly** - Restrict origins in production
4. **Use HTTPS** - Configure SSL certificates
5. **Regular updates** - Keep dependencies updated
6. **Monitor logs** - Set up log monitoring and alerts

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -h 72.62.196.30 -u myuser -p cab_app
```

**Service Won't Start:**
```bash
# Check logs
sudo journalctl -u cab-api -n 50

# Check file permissions
ls -la /home/ubuntu/cab_app/
```

**Port Already in Use:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

## 📞 Support

For issues and questions:
- Check logs: `sudo journalctl -u cab-api -f`
- Verify database connection
- Check environment variables
- Review API documentation at `/docs`

## 🎯 Next Steps

- [ ] Add authentication and authorization
- [ ] Implement real-time notifications
- [ ] Add payment gateway integration
- [ ] Set up monitoring and alerting
- [ ] Add rate limiting
- [ ] Implement caching
- [ ] Add comprehensive testing

---

**Built with ❤️ using FastAPI and MySQL**
