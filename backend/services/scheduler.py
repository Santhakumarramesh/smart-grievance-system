"""
Background Scheduler for periodic tasks
Runs comment escalation checks every hour
"""
import threading
import time
from datetime import datetime
from backend.services.comment_escalation import check_and_escalate_comments

class BackgroundScheduler:
    """Simple background scheduler for running periodic tasks"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.thread = None
    
    def init_app(self, app):
        """Initialize with Flask app context"""
        self.app = app
    
    def start(self):
        """Start the background scheduler"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("✓ Background scheduler started - Checking comment escalations every hour")
    
    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _run_scheduler(self):
        """Main scheduler loop - runs every hour"""
        while self.running:
            try:
                # Wait for 1 hour (3600 seconds)
                # For testing, you can reduce this to 60 seconds
                time.sleep(3600)  # 1 hour
                
                if not self.running:
                    break
                
                # Run escalation check within app context
                if self.app:
                    with self.app.app_context():
                        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running comment escalation check...")
                        escalated_count = check_and_escalate_comments()
                        
                        if escalated_count > 0:
                            print(f"✓ Escalated {escalated_count} overdue comments")
                        else:
                            print("✓ No comments need escalation")
                
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                # Continue running even if there's an error
                continue

# Global scheduler instance
scheduler = BackgroundScheduler()
