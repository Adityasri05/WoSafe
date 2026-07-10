"""
WoSafe WebSocket — Connection Manager & Routes
Real-time communication for journeys, emergencies, guardian tracking, and notifications.
"""

import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections with room-based routing."""

    def __init__(self):
        # room_id -> set of WebSocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}
        # user_id -> WebSocket
        self.user_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str, room: str | None = None):
        """Accept a WebSocket connection and add to room."""
        await websocket.accept()
        self.user_connections[user_id] = websocket

        if room:
            if room not in self.active_connections:
                self.active_connections[room] = set()
            self.active_connections[room].add(websocket)

        logger.info(f"WebSocket connected: user={user_id}, room={room}")

    def disconnect(self, websocket: WebSocket, user_id: str, room: str | None = None):
        """Remove a WebSocket connection."""
        self.user_connections.pop(user_id, None)
        if room and room in self.active_connections:
            self.active_connections[room].discard(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to a specific user."""
        ws = self.user_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self.user_connections.pop(user_id, None)

    async def broadcast_to_room(self, room: str, message: dict, exclude: WebSocket | None = None):
        """Broadcast a message to all connections in a room."""
        connections = self.active_connections.get(room, set()).copy()
        disconnected = set()
        for ws in connections:
            if ws == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        # Clean up disconnected
        for ws in disconnected:
            self.active_connections.get(room, set()).discard(ws)

    async def broadcast_all(self, message: dict):
        """Broadcast to all connected users."""
        for user_id, ws in list(self.user_connections.items()):
            try:
                await ws.send_json(message)
            except Exception:
                self.user_connections.pop(user_id, None)

    @property
    def connection_count(self) -> int:
        return len(self.user_connections)


# ── Singleton Manager ──────────────────────
manager = ConnectionManager()


# ── WebSocket Routes ───────────────────────
ws_router = APIRouter()


@ws_router.websocket("/ws/journey/{user_id}")
async def journey_websocket(websocket: WebSocket, user_id: str):
    """Live journey updates — location, safety score, events."""
    room = f"journey:{user_id}"
    await manager.connect(websocket, user_id, room)
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type", "location_update")

            if event_type == "location_update":
                await manager.broadcast_to_room(room, {
                    "type": "location_update",
                    "user_id": user_id,
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "speed": data.get("speed"),
                    "timestamp": datetime.now(UTC).isoformat(),
                }, exclude=websocket)

            elif event_type == "safety_update":
                await manager.broadcast_to_room(room, {
                    "type": "safety_update",
                    "safety_score": data.get("safety_score"),
                    "risk_level": data.get("risk_level"),
                    "timestamp": datetime.now(UTC).isoformat(),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, room)


@ws_router.websocket("/ws/emergency/{session_id}")
async def emergency_websocket(websocket: WebSocket, session_id: str):
    """Live emergency updates — location, status, responders."""
    room = f"emergency:{session_id}"
    user_id = f"emergency-{session_id}"
    await manager.connect(websocket, user_id, room)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_room(room, {
                "type": data.get("type", "emergency_update"),
                "session_id": session_id,
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            }, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, room)


@ws_router.websocket("/ws/guardian/{user_id}")
async def guardian_websocket(websocket: WebSocket, user_id: str):
    """Guardian tracking — live location of protected user."""
    room = f"guardian:{user_id}"
    await manager.connect(websocket, f"guardian-{user_id}", room)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_room(room, {
                "type": "guardian_update",
                "user_id": user_id,
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            }, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"guardian-{user_id}", room)


@ws_router.websocket("/ws/community")
async def community_websocket(websocket: WebSocket):
    """Community feed — live reports and incidents."""
    room = "community:feed"
    user_id = f"community-{id(websocket)}"
    await manager.connect(websocket, user_id, room)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_room(room, {
                "type": "community_update",
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            }, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, room)


@ws_router.websocket("/ws/notifications/{user_id}")
async def notifications_websocket(websocket: WebSocket, user_id: str):
    """User notification stream."""
    await manager.connect(websocket, f"notif-{user_id}")
    try:
        while True:
            await websocket.receive_text()  # Keep-alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"notif-{user_id}")
