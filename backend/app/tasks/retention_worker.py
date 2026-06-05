from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.emotion_log import EmotionLog

def cleanup_old_logs(db: Session):
    """
    Cleans up/anonymizes raw AI responses that are older than 30 days
    to comply with the data retention policy.
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Update raw_ai_response to None for logs older than 30 days
    db.query(EmotionLog).filter(EmotionLog.created_at < thirty_days_ago).update(
        {EmotionLog.raw_ai_response: None},
        synchronize_session=False
    )
    db.commit()
