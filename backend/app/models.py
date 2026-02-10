# app/models.py

import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Float,
    Enum,
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


# ---------------------------
# Enums
# ---------------------------

class PlacementMethod(str, enum.Enum):
    manual = "manual"
    gps_suggested = "gps_suggested"


# ---------------------------
# User
# ---------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_uid = Column(String, unique=True, nullable=False, index=True)

    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("Project", back_populates="owner")



# ---------------------------
# Project
# ---------------------------

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    


    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="projects")

    plans = relationship(
        "Plan",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    photos = relationship(
        "Photo",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# ---------------------------
# Plan (PDF → PNG)
# ---------------------------

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # PNG stored in Supabase Storage
    file_url = Column(String, nullable=False)

    # Raster dimensions (for plan viewer)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="plans")

    photo_placements = relationship(
        "PhotoPlacement",
        back_populates="plan",
        cascade="all, delete-orphan",
    )


# ---------------------------
# Photo (with EXIF)
# ---------------------------

class Photo(Base):
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # JPEG stored in Supabase Storage
    file_url = Column(String, nullable=False)

    # EXIF metadata
    exif_lat = Column(Float, nullable=True)
    exif_lng = Column(Float, nullable=True)
    exif_timestamp = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="photos")

    placements = relationship(
        "PhotoPlacement",
        back_populates="photo",
        cascade="all, delete-orphan",
    )


# ---------------------------
# Photo Placement (pins)
# ---------------------------

class PhotoPlacement(Base):
    __tablename__ = "photo_placements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("photos.id", ondelete="CASCADE"),
        nullable=False,
    )

    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Coordinates on plan (pixels for MVP)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)

    placement_method = Column(
        Enum(PlacementMethod, name="placement_method_enum"),
        nullable=False,
        default=PlacementMethod.manual,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    photo = relationship("Photo", back_populates="placements")
    plan = relationship("Plan", back_populates="photo_placements")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    file_url = Column(String, nullable=False)
    file_type = Column(String, default="html")  # html or pdf

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="reports")
