"""
WoSafe Backend — Database Seeding Script
Populates the database with sample data: users, emergency contacts,
police stations, hospitals, safe locations, and incident reports.
"""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    User,
    EmergencyContact,
    PoliceStation,
    Hospital,
    SafeLocation,
    Incident,
    CommunityReport,
    SafetyHeatmap,
)
from app.database.base import Base

# Setup engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def seed():
    print("Starting database seeding...")
    async with async_session() as session:
        async with session.begin():
            # ── 1. Seed Users ───────────────────────
            print("Seeding users...")
            
            # Admin User
            admin = await session.execute(select(User).where(User.email == "admin@wosafe.app"))
            if not admin.scalars().first():
                admin_user = User(
                    name="System Administrator",
                    email="admin@wosafe.app",
                    password_hash=hash_password("admin_password"),
                    role="admin",
                    is_verified=True,
                )
                session.add(admin_user)

            # Normal User
            normal = await session.execute(select(User).where(User.email == "jane@wosafe.app"))
            jane = normal.scalars().first()
            if not jane:
                jane = User(
                    name="Jane Doe",
                    email="jane@wosafe.app",
                    password_hash=hash_password("jane_password"),
                    phone="+15550199",
                    role="user",
                    safe_word="pineapple",
                    is_verified=True,
                    blood_group="O+",
                    medical_conditions="Penicillin allergy",
                    last_latitude=37.7749,
                    last_longitude=-122.4194,
                    last_address="Market Street, San Francisco, CA",
                )
                session.add(jane)

            # Volunteer User
            volunteer = await session.execute(select(User).where(User.email == "volunteer@wosafe.app"))
            if not volunteer.scalars().first():
                volunteer_user = User(
                    name="Sarah Connor",
                    email="volunteer@wosafe.app",
                    password_hash=hash_password("volunteer_password"),
                    phone="+15550200",
                    role="volunteer",
                    is_verified=True,
                    is_active=True,
                    last_latitude=37.7891,
                    last_longitude=-122.4014,
                    last_address="Union Square, San Francisco, CA",
                )
                session.add(volunteer_user)

            # ── 2. Seed Emergency Contacts ──────────
            print("Seeding emergency contacts...")
            await session.flush()  # Ensure jane.id is generated
            
            contact_check = await session.execute(select(EmergencyContact).where(EmergencyContact.phone == "+15550300"))
            if not contact_check.scalars().first():
                contact = EmergencyContact(
                    user_id=jane.id,
                    name="John Doe",
                    phone="+15550300",
                    relation="spouse",
                    priority=1,
                    notify_sms=True,
                    notify_call=True,
                    notify_push=True,
                )
                session.add(contact)

            # ── 3. Seed Police Stations ─────────────
            print("Seeding police stations...")
            police_check = await session.execute(select(PoliceStation).where(PoliceStation.name == "SFPD Tenderloin Station"))
            if not police_check.scalars().first():
                tenderloin_station = PoliceStation(
                    name="SFPD Tenderloin Station",
                    latitude=37.7837,
                    longitude=-122.4129,
                    address="301 Eddy St, San Francisco, CA 94102",
                    phone="+14155531344",
                    is_24hr=True,
                    has_women_desk=True,
                )
                session.add(tenderloin_station)

                mission_station = PoliceStation(
                    name="SFPD Mission Station",
                    latitude=37.7628,
                    longitude=-122.4220,
                    address="630 Valencia St, San Francisco, CA 94110",
                    phone="+14155531912",
                    is_24hr=True,
                    has_women_desk=True,
                )
                session.add(mission_station)

            # ── 4. Seed Hospitals ───────────────────
            print("Seeding hospitals...")
            hospital_check = await session.execute(select(Hospital).where(Hospital.name == "Zuckerberg San Francisco General Hospital"))
            if not hospital_check.scalars().first():
                sfg_hospital = Hospital(
                    name="Zuckerberg San Francisco General Hospital",
                    latitude=37.7554,
                    longitude=-122.4048,
                    address="1001 Potrero Ave, San Francisco, CA 94110",
                    phone="+16282062300",
                    emergency_phone="+16282068000",
                    has_trauma_center=True,
                )
                session.add(sfg_hospital)

            # ── 5. Seed Safe Locations ──────────────
            print("Seeding safe locations...")
            safe_check = await session.execute(select(SafeLocation).where(SafeLocation.name == "Market Street 24/7 Pharmacy"))
            if not safe_check.scalars().first():
                pharmacy = SafeLocation(
                    name="Market Street 24/7 Pharmacy",
                    location_type="safe_business",
                    latitude=37.7785,
                    longitude=-122.4150,
                    address="1201 Market St, San Francisco, CA 94103",
                    phone="+14155550190",
                    is_24hr=True,
                    safety_rating=4.8,
                )
                session.add(pharmacy)

                shelter = SafeLocation(
                    name="Women's Safety Shelter SF",
                    location_type="shelter",
                    latitude=37.7700,
                    longitude=-122.4300,
                    address="San Francisco, CA",
                    phone="+14155550299",
                    is_24hr=True,
                    safety_rating=5.0,
                )
                session.add(shelter)

            # ── 6. Seed Incidents ───────────────────
            print("Seeding incidents...")
            incident_check = await session.execute(select(Incident).where(Incident.title == "Unsafe Street Lighting"))
            if not incident_check.scalars().first():
                incident = Incident(
                    reporter_id=jane.id,
                    category="unsafe_area",
                    title="Unsafe Street Lighting",
                    description="All streetlights are broken on this block. Extremely dark and unsafe at night.",
                    severity="medium",
                    status="reported",
                    latitude=37.7810,
                    longitude=-122.4110,
                    address="Golden Gate Ave & Hyde St, San Francisco, CA",
                    is_anonymous=False,
                    votes_count=12,
                    verification_count=3,
                )
                session.add(incident)

                harassment = Incident(
                    category="harassment",
                    title="Verbal harassment near BART exit",
                    description="A group of individuals harassing passersby, particularly women walking alone.",
                    severity="high",
                    status="reported",
                    latitude=37.7794,
                    longitude=-122.4138,
                    address="Civic Center BART Station, San Francisco, CA",
                    is_anonymous=True,
                    votes_count=28,
                    verification_count=8,
                )
                session.add(harassment)

            # ── 7. Seed Heatmap points ──────────────
            print("Seeding safety heatmap points...")
            heatmap_check = await session.execute(select(SafetyHeatmap).where(SafetyHeatmap.latitude == 37.7810))
            if not heatmap_check.scalars().first():
                pt1 = SafetyHeatmap(
                    latitude=37.7810,
                    longitude=-122.4110,
                    grid_hash="hash1",
                    risk_score=6.5,
                    incident_count=3,
                    report_count=2,
                    factors_json={"lighting": "poor", "crowd": "low"},
                )
                session.add(pt1)

                pt2 = SafetyHeatmap(
                    latitude=37.7794,
                    longitude=-122.4138,
                    grid_hash="hash2",
                    risk_score=8.2,
                    incident_count=8,
                    report_count=5,
                    factors_json={"harassment": "high", "crowd": "moderate"},
                )
                session.add(pt2)

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
