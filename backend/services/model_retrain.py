"""
Model retraining service.
Supports manual trigger (admin) and scheduled retraining.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

from backend.config import Config


RETRAIN_LOCK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'ml', 'artifacts', 'retrain.lock'
)
RETRAIN_LOCK_STALE_SECONDS = 60 * 30


def reload_classifier():
    """Reload the ML classifier with newly trained model (call after retrain)."""
    try:
        from backend.services.classifier import classifier
        classifier.load_model()
        return True
    except Exception:
        return False


def get_retrain_status():
    """Get last training metadata if available."""
    from backend.services.classifier import classifier

    metadata = None
    try:
        if os.path.exists(Config.MODEL_METADATA_PATH):
            with open(Config.MODEL_METADATA_PATH, 'r', encoding='utf-8') as metadata_file:
                metadata = json.load(metadata_file)
    except Exception:
        metadata = None

    return {
        'runtime': classifier.get_runtime_status(),
        'latest_training': metadata,
        'policy': {
            'auto_assign_confidence_threshold': Config.ML_AUTO_ASSIGN_CONFIDENCE_THRESHOLD,
            'manual_review_department': Config.ML_MANUAL_REVIEW_DEPARTMENT,
        }
    }


def _is_lock_stale(path):
    try:
        modified_at = os.path.getmtime(path)
    except OSError:
        return False
    return (datetime.utcnow().timestamp() - modified_at) > RETRAIN_LOCK_STALE_SECONDS


def _acquire_retrain_lock():
    os.makedirs(os.path.dirname(RETRAIN_LOCK_PATH), exist_ok=True)

    if os.path.exists(RETRAIN_LOCK_PATH):
        if _is_lock_stale(RETRAIN_LOCK_PATH):
            try:
                os.remove(RETRAIN_LOCK_PATH)
            except OSError:
                return False
        else:
            return False

    try:
        with open(RETRAIN_LOCK_PATH, 'x', encoding='utf-8') as lock_file:
            lock_file.write(datetime.utcnow().isoformat())
        return True
    except Exception:
        return False


def _release_retrain_lock():
    try:
        if os.path.exists(RETRAIN_LOCK_PATH):
            os.remove(RETRAIN_LOCK_PATH)
    except OSError:
        pass


def retrain_model(trigger='manual'):
    """
    Run model retraining. Returns (success: bool, message: str).
    """
    if not _acquire_retrain_lock():
        return False, "Retraining already in progress"

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    train_script = os.path.join(project_root, 'ml', 'train.py')
    
    if not os.path.exists(train_script):
        _release_retrain_lock()
        return False, "Training script not found"
    
    try:
        result = subprocess.run(
            [sys.executable, train_script],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 min max
        )
        
        if result.returncode == 0:
            reload_classifier()
            training_payload = get_retrain_status().get('latest_training') or {}
            if training_payload:
                training_payload['last_reload_at_utc'] = datetime.utcnow().isoformat()
                training_payload['last_retrain_trigger'] = trigger
                with open(Config.MODEL_METADATA_PATH, 'w', encoding='utf-8') as metadata_file:
                    json.dump(training_payload, metadata_file, indent=2)
            acc = float(training_payload.get('metrics', {}).get('accuracy', 0.0)) * 100
            return True, f"Model retrained successfully. Accuracy: {acc:.2f}%"
        else:
            err = result.stderr or result.stdout or "Unknown error"
            return False, f"Training failed: {err[:500]}"
    except subprocess.TimeoutExpired:
        return False, "Training timed out (5 min)"
    except Exception as e:
        return False, str(e)
    finally:
        _release_retrain_lock()
