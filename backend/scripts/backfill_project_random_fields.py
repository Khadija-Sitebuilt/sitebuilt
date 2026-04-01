import random
import sys
from datetime import date, timedelta

from sqlalchemy import inspect

from app.database import SessionLocal, engine
from app import models


RANDOM_MANAGERS = [
    "Aarav Shah",
    "Isha Mehta",
    "Rohan Patel",
    "Neha Kapoor",
    "Vikram Rao",
    "Sara Khan",
    "Arjun Menon",
    "Kiran Desai",
]

RANDOM_BUDGETS = [
    "250000",
    "350000",
    "500000",
    "750000",
    "1000000",
    "1250000",
]


def ensure_columns():
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("projects")}
    required = {
        "location",
        "start_date",
        "end_date",
        "project_manager",
        "estimated_budget",
    }
    missing = required - columns
    if missing:
        print(f"Missing columns in projects table: {sorted(missing)}")
        print("Run alembic migrations first (0004_add_project_fields).")
        return False
    return True


def backfill():
    db = SessionLocal()
    try:
        projects = db.query(models.Project).all()
        updated = 0

        for project in projects:
            changed = False

            if not project.project_manager:
                if project.owner and project.owner.full_name:
                    project.project_manager = project.owner.full_name
                else:
                    project.project_manager = random.choice(RANDOM_MANAGERS)
                changed = True

            if not project.estimated_budget:
                project.estimated_budget = random.choice(RANDOM_BUDGETS)
                changed = True

            if not project.start_date and not project.end_date:
                base = project.created_at.date() if project.created_at else date.today()
                project.start_date = base
                project.end_date = base + timedelta(days=random.randint(7, 60))
                changed = True
            elif project.start_date and not project.end_date:
                project.end_date = project.start_date + timedelta(days=random.randint(7, 60))
                changed = True
            elif not project.start_date and project.end_date:
                project.start_date = project.end_date - timedelta(days=random.randint(7, 60))
                changed = True

            if changed:
                updated += 1

        db.commit()

        missing_budget = (
            db.query(models.Project)
            .filter(models.Project.estimated_budget.is_(None))
            .count()
        )
        missing_timeline = (
            db.query(models.Project)
            .filter(models.Project.start_date.is_(None))
            .filter(models.Project.end_date.is_(None))
            .count()
        )
        missing_team = (
            db.query(models.Project)
            .filter(models.Project.project_manager.is_(None))
            .count()
        )

        print(f"Random backfill complete. Updated {updated} projects.")
        print(f"Projects missing budget: {missing_budget}")
        print(f"Projects missing timeline: {missing_timeline}")
        print(f"Projects missing project_manager: {missing_team}")
        return 0
    finally:
        db.close()


def main() -> int:
    if not ensure_columns():
        return 1
    return backfill()


if __name__ == "__main__":
    sys.exit(main())
