import uuid
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models
from .storage import upload_file, get_public_url

def generate_export(project: models.Project, db: Session) -> str:
    plans = project.plans
    photos = project.photos

    if not plans:
        raise ValueError("No plans found for project")

    plan = plans[0]  # MVP: first plan only

    rows = []
    counter = 1

    for photo in photos:
        for placement in photo.placements:
            rows.append({
                "num": counter,
                "timestamp": photo.exif_timestamp,
                "x": placement.x,
                "y": placement.y,
                "method": placement.placement_method.value,
            })
            counter += 1

    html = build_html(project, plan, rows)

    filename = f"{project.id}/export_{uuid.uuid4()}.html"

    upload_file(
        bucket="exports",
        path=filename,
        content=html.encode("utf-8"),
        content_type="text/html",
    )

    return get_public_url("exports", filename)


def build_html(project, plan, rows):
    table_rows = ""
    for r in rows:
        table_rows += f"""
        <tr>
            <td>{r['num']}</td>
            <td>{r['timestamp'] or ''}</td>
            <td>{round(r['x'], 2)}</td>
            <td>{round(r['y'], 2)}</td>
            <td>{r['method']}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>As-Built Export</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            img {{ max-width: 100%; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Project: {project.name}</h1>
        <p>Generated at: {datetime.utcnow()}</p>

        <h2>Floor Plan</h2>
        <img src="{plan.file_url}" />

        <h2>Photo Placements</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Timestamp</th>
                <th>X</th>
                <th>Y</th>
                <th>Method</th>
            </tr>
            {table_rows}
        </table>
    </body>
    </html>
    """

