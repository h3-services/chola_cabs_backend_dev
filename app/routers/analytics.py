"""
Analytics API endpoints for admin dashboard
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models import Trip, Driver, WalletTransaction
from app.schemas import (
    DashboardSummaryResponse, MonthlyRevenueResponse, MonthlyRevenueItem,
    VehicleTypeRevenueResponse, VehicleTypeRevenueItem
)
from decimal import Decimal
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    try:
        # Total revenue from completed trips (Commission)
        total_revenue = db.query(func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None
        ).scalar() or Decimal('0')
        
        # Today's revenue
        today = date.today()
        today_revenue = db.query(func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None,
            func.date(WalletTransaction.created_at) == today
        ).scalar() or Decimal('0')
        
        # Total trips
        total_trips = db.query(func.count(Trip.trip_id)).scalar() or 0
        
        # Today's trips
        today_trips = db.query(func.count(Trip.trip_id)).filter(
            func.date(Trip.created_at) == today
        ).scalar() or 0
        
        # Driver statistics
        total_drivers = db.query(func.count(Driver.driver_id)).scalar() or 0
        active_drivers = db.query(func.count(Driver.driver_id)).filter(
            Driver.is_available == True,
            Driver.is_approved == True
        ).scalar() or 0
        
        # Trip status counts
        completed_trips = db.query(func.count(Trip.trip_id)).filter(
            Trip.trip_status == "COMPLETED"
        ).scalar() or 0
        
        cancelled_trips = db.query(func.count(Trip.trip_id)).filter(
            Trip.trip_status == "CANCELLED"
        ).scalar() or 0
        
        # Assigned trips (ASSIGNED or STARTED status)
        assigned_trips = db.query(func.count(Trip.trip_id)).filter(
            Trip.trip_status.in_(["ASSIGNED", "STARTED"])
        ).scalar() or 0
        
        # Pending trips (OPEN status)
        pending_trips = db.query(func.count(Trip.trip_id)).filter(
            Trip.trip_status == "OPEN"
        ).scalar() or 0
        
        # In progress trips (STARTED status)
        in_progress_trips = db.query(func.count(Trip.trip_id)).filter(
            Trip.trip_status == "STARTED"
        ).scalar() or 0
        
        return DashboardSummaryResponse(
            total_revenue=total_revenue,
            today_revenue=today_revenue,
            total_trips=total_trips,
            today_trips=today_trips,
            active_drivers=active_drivers,
            total_drivers=total_drivers,
            completed_trips=completed_trips,
            cancelled_trips=cancelled_trips,
            assigned_trips=assigned_trips,
            pending_trips=pending_trips,
            in_progress_trips=in_progress_trips
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/revenue/monthly", response_model=MonthlyRevenueResponse)
def get_monthly_revenue(
    year: int = Query(..., description="Year for monthly revenue breakdown"),
    db: Session = Depends(get_db)
):
    """Get monthly revenue breakdown for a specific year"""
    try:
        # Query monthly revenue data (Commission only)
        monthly_data = db.query(
            extract('month', WalletTransaction.created_at).label('month'),
            func.sum(WalletTransaction.amount).label('revenue'),
            func.count(WalletTransaction.trip_id).label('trips')
        ).filter(
            extract('year', WalletTransaction.created_at) == year,
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None
        ).group_by(
            extract('month', WalletTransaction.created_at)
        ).all()
        
        # Month names mapping
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        # Create monthly revenue items
        monthly_revenue = []
        total_year_revenue = Decimal('0')
        total_year_trips = 0
        
        # Initialize all months with zero values
        for month in range(1, 13):
            monthly_revenue.append(MonthlyRevenueItem(
                month=month,
                month_name=month_names[month],
                revenue=Decimal('0'),
                trips=0
            ))
        
        # Fill in actual data
        for data in monthly_data:
            month_idx = int(data.month) - 1
            revenue = data.revenue or Decimal('0')
            trips = data.trips or 0
            
            monthly_revenue[month_idx] = MonthlyRevenueItem(
                month=int(data.month),
                month_name=month_names[int(data.month)],
                revenue=revenue,
                trips=trips
            )
            total_year_revenue += revenue
            total_year_trips += trips
        
        return MonthlyRevenueResponse(
            year=year,
            monthly_revenue=monthly_revenue,
            total_year_revenue=total_year_revenue,
            total_year_trips=total_year_trips
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/revenue/vehicle-type", response_model=VehicleTypeRevenueResponse)
def get_revenue_by_vehicle_type(
    year: Optional[int] = Query(None, description="Year filter (optional)"),
    db: Session = Depends(get_db)
):
    """Get revenue breakdown by vehicle type"""
    try:
        # Base query (Commission only)
        query = db.query(
            Trip.vehicle_type,
            func.sum(WalletTransaction.amount).label('revenue'),
            func.count(Trip.trip_id).label('trips')
        ).join(
            WalletTransaction, Trip.trip_id == WalletTransaction.trip_id
        ).filter(
            WalletTransaction.transaction_type == "DEBIT",
            Trip.trip_status == "COMPLETED"
        )
        
        # Add year filter if provided
        if year:
            query = query.filter(extract('year', Trip.created_at) == year)
        
        # Group by vehicle type
        vehicle_data = query.group_by(Trip.vehicle_type).all()
        
        # Calculate total revenue for percentage calculation
        total_revenue = sum(data.revenue or Decimal('0') for data in vehicle_data)
        
        # Create vehicle type revenue items
        vehicle_revenue = []
        for data in vehicle_data:
            revenue = data.revenue or Decimal('0')
            trips = data.trips or 0
            percentage = float(revenue / total_revenue * 100) if total_revenue > 0 else 0.0
            
            vehicle_revenue.append(VehicleTypeRevenueItem(
                vehicle_type=data.vehicle_type or "Unknown",
                revenue=revenue,
                trips=trips,
                percentage=round(percentage, 2)
            ))
        
        # Sort by revenue descending
        vehicle_revenue.sort(key=lambda x: x.revenue, reverse=True)
        
        return VehicleTypeRevenueResponse(
            vehicle_revenue=vehicle_revenue,
            total_revenue=total_revenue
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/revenue/12-months")
def get_12_months_revenue(db: Session = Depends(get_db)):
    """Get revenue for the last 12 months from current date"""
    try:
        current_date = date.today()
        start_date = current_date - relativedelta(months=11)
        start_date = start_date.replace(day=1)  # Start from first day of month
        
        # Query monthly revenue for last 12 months (Commission only)
        monthly_data = db.query(
            extract('year', WalletTransaction.created_at).label('year'),
            extract('month', WalletTransaction.created_at).label('month'),
            func.sum(WalletTransaction.amount).label('revenue'),
            func.count(WalletTransaction.trip_id).label('trips')
        ).filter(
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None,
            func.date(WalletTransaction.created_at) >= start_date
        ).group_by(
            extract('year', WalletTransaction.created_at),
            extract('month', WalletTransaction.created_at)
        ).order_by(
            extract('year', WalletTransaction.created_at),
            extract('month', WalletTransaction.created_at)
        ).all()
        
        # Month names mapping
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        
        # Create 12-month data structure
        months_revenue = []
        total_revenue = Decimal('0')
        total_trips = 0
        
        # Generate all 12 months
        for i in range(12):
            month_date = start_date + relativedelta(months=i)
            months_revenue.append({
                "year": month_date.year,
                "month": month_date.month,
                "month_name": month_names[month_date.month],
                "month_year": f"{month_names[month_date.month]} {month_date.year}",
                "revenue": Decimal('0'),
                "trips": 0
            })
        
        # Fill in actual data
        for data in monthly_data:
            year, month = int(data.year), int(data.month)
            revenue = data.revenue or Decimal('0')
            trips = data.trips or 0
            
            # Find matching month in our structure
            for month_item in months_revenue:
                if month_item["year"] == year and month_item["month"] == month:
                    month_item["revenue"] = revenue
                    month_item["trips"] = trips
                    total_revenue += revenue
                    total_trips += trips
                    break
        
        return {
            "period": "Last 12 Months",
            "start_date": start_date,
            "end_date": current_date,
            "total_revenue": total_revenue,
            "total_trips": total_trips,
            "monthly_data": months_revenue
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/revenue/range")
def get_revenue_by_date_range(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get revenue for a specific date range"""
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        # Query revenue in date range (Commission only)
        revenue_data = db.query(
            func.sum(WalletTransaction.amount).label('total_revenue'),
            func.count(WalletTransaction.trip_id).label('total_trips')
        ).filter(
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None,
            func.date(WalletTransaction.created_at) >= start_date,
            func.date(WalletTransaction.created_at) <= end_date
        ).first()
        
        # Daily breakdown
        daily_data = db.query(
            func.date(WalletTransaction.created_at).label('date'),
            func.sum(WalletTransaction.amount).label('revenue'),
            func.count(WalletTransaction.trip_id).label('trips')
        ).filter(
            WalletTransaction.transaction_type == "DEBIT",
            WalletTransaction.trip_id != None,
            func.date(WalletTransaction.created_at) >= start_date,
            func.date(WalletTransaction.created_at) <= end_date
        ).group_by(
            func.date(WalletTransaction.created_at)
        ).all()
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": revenue_data.total_revenue or Decimal('0'),
            "total_trips": revenue_data.total_trips or 0,
            "daily_breakdown": [
                {
                    "date": data.date,
                    "revenue": data.revenue or Decimal('0'),
                    "trips": data.trips or 0
                }
                for data in daily_data
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )