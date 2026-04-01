import sys
from sqlalchemy import inspect

from app.database import SessionLocal, engine
from app import models


def main() -> int:
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
        return 1

    db = SessionLocal()
    try:
        # Backfill project_manager from owner full_name if missing
        projects = (
            db.query(models.Project)
            .filter(models.Project.project_manager.is_(None))
            .all()
        )

        updated = 0
        for project in projects:
            if project.owner and project.owner.full_name:
                project.project_manager = project.owner.full_name
                updated += 1

        db.commit()

        # Report remaining gaps (no changes)
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

        print(f"Backfill complete. Updated project_manager for {updated} projects.")
        print(f"Projects missing budget: {missing_budget}")
        print(f"Projects missing timeline: {missing_timeline}")
        print(f"Projects missing project_manager: {missing_team}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
