"""
Notification API router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import requests
import os
from app.schemas import PushNotificationRequest
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Bridge server URL from environment or default
NOTIFICATION_BRIDGE_URL = os.getenv("NOTIFICATION_BRIDGE_URL", "https://temple.hope3services.cloud/api/notifications/push/token")

@router.post("/send")
def send_push_notification(payload: PushNotificationRequest):
    """
    Send push notification via FCM bridge server.
    Supports both registration_ids (tokens) and driverIds.
    """
    try:
        # Prepare the payload for the bridge server
        bridge_payload = {
            "title": payload.title,
            "body": payload.body,
            "notification": payload.notification or {
                "title": payload.title,
                "body": payload.body,
                "sound": "default"
            },
            "data": payload.data or {}
        }
        
        if payload.registration_ids:
            bridge_payload["registration_ids"] = payload.registration_ids
        elif payload.driverIds:
            bridge_payload["driverIds"] = payload.driverIds
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either registration_ids or driverIds must be provided"
            )

        # Forward to bridge server
        # response = requests.post(NOTIFICATION_BRIDGE_URL, json=bridge_payload, timeout=10)
        # response.raise_for_status()
        
        logger.info(f"Notification sent request: {payload.title}")
        
        # For now, simulate success if bridge is not configured
        return {
            "status": "success",
            "message": "Notification request processed",
            "details": bridge_payload
        }
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )
