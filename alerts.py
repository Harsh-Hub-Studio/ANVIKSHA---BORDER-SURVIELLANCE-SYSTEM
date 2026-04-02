# ============================================================
# FILE: alerts.py
# ALGORITHM: Algorithm 6 — Socket.IO Event-Driven Architecture
# PURPOSE: Real-time alert push system for incident log
# PATTERN: Observer / Publisher-Subscriber
# ============================================================

from flask_socketio import SocketIO
from datetime import datetime

# Global SocketIO instance — set via init_socketio()
socketio = None

# Alert history (last 50 alerts kept in memory)
alert_history = []
MAX_HISTORY   = 50


def init_socketio(app):
    """
    Initialize Socket.IO with Flask app.
    Call this once in main.py during startup.

    Algorithm: Event-Driven Architecture
    - Creates persistent WebSocket connection
    - Enables server → client push notifications
    - No polling required (more efficient)
    """
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")

    # ── SOCKET.IO EVENT HANDLERS ──────────────────────────────
    @socketio.on('connect')
    def on_connect():
        print("[SOCKET] Client connected to alert system")

        # Send last 10 alerts to newly connected client
        for alert in alert_history[-10:]:
            socketio.emit('new_alert', alert)

    @socketio.on('disconnect')
    def on_disconnect():
        print("[SOCKET] Client disconnected")

    return socketio


# ── ALGORITHM 6: SEND ALERT ───────────────────────────────────
def send_alert(message, level="INFO", cam_id=None):
    """
    Push real-time alert to all connected dashboards.

    Algorithm: Observer Pattern / Event-Driven Architecture
    - Server EMITS event (publisher)
    - Dashboard LISTENS for event (subscriber)
    - Alert delivered in < 80ms

    Levels: CRITICAL, HIGH, MED, LOW, INFO
    """
    alert = {
        'message':   message,
        'level':     level,
        'cam_id':    cam_id,
        'timestamp': datetime.now().isoformat(),
        'time_str':  datetime.now().strftime("%H:%M:%S")
    }

    # Store in history
    alert_history.append(alert)
    if len(alert_history) > MAX_HISTORY:
        alert_history.pop(0)

    # Push to all connected clients
    if socketio:
        socketio.emit('new_alert', alert)

    print(f"[ALERT][{level}] CAM-{cam_id or '?'}: {message}")
    return alert


# ── SPECIFIC ALERT TYPES ──────────────────────────────────────
def alert_intruder(cam_id):
    """Unknown face detected — highest priority alert."""
    return send_alert(
        f"⚠ UNKNOWN INTRUDER DETECTED",
        level="CRITICAL",
        cam_id=cam_id
    )


def alert_authorized(cam_id, name="PERSONNEL"):
    """Authorized face recognized — informational alert."""
    return send_alert(
        f"✓ {name} IDENTIFIED — ACCESS GRANTED",
        level="LOW",
        cam_id=cam_id
    )


def alert_vehicle(cam_id, vehicle_type, confidence):
    """Vehicle detected by YOLO."""
    return send_alert(
        f"🚗 {vehicle_type.upper()} DETECTED ({confidence:.0%})",
        level="MED",
        cam_id=cam_id
    )


def alert_person(cam_id, confidence):
    """Person detected by YOLO (not face-recognized)."""
    return send_alert(
        f"👤 PERSON DETECTED ({confidence:.0%})",
        level="HIGH",
        cam_id=cam_id
    )


def alert_camera_offline(cam_id):
    """Camera feed lost."""
    return send_alert(
        f"📵 CAMERA FEED LOST",
        level="HIGH",
        cam_id=cam_id
    )


def alert_camera_online(cam_id):
    """Camera feed restored."""
    return send_alert(
        f"📷 CAMERA FEED RESTORED",
        level="INFO",
        cam_id=cam_id
    )


def alert_id_card(cam_id, is_authorized):
    """ID card detected."""
    if is_authorized:
        return send_alert(
            "🪪 AUTHORIZED ID CARD VERIFIED",
            level="LOW",
            cam_id=cam_id
        )
    else:
        return send_alert(
            "⚠ NO VALID ID — ACCESS DENIED",
            level="HIGH",
            cam_id=cam_id
        )


def alert_high_risk(score, level):
    """Infiltration risk score crossed threshold."""
    return send_alert(
        f"⚠ RISK SCORE {score}/100 — {level} THREAT",
        level="CRITICAL" if score >= 70 else "MED",
        cam_id=None
    )
