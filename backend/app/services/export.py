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
                "photo_url": photo.file_url,
                "lat": photo.exif_lat,
                "lng": photo.exif_lng,
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
        photo_cell = f'<a href="{r["photo_url"]}" target="_blank"><img src="{r["photo_url"]}" style="max-width: 50px; max-height: 50px; border-radius: 4px; cursor: pointer;" alt="Photo {r["num"]}" title="Click to view full photo"></a>' if r["photo_url"] else "—"
        
        location_info = ""
        if r["lat"] and r["lng"]:
            location_info = f'<small style="display: block; color: #666;">Lat: {r["lat"]:.4f}, Lng: {r["lng"]:.4f}</small>'
        
        table_rows += f"""
        <tr>
            <td class="center"><strong>{r['num']}</strong></td>
            <td><span class="badge">{r['method'].upper()}</span></td>
            <td class="center">{photo_cell}</td>
            <td class="center">{r['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if r['timestamp'] else '—'}{location_info}</td>
            <td class="center">{round(r['x'], 1)}</td>
            <td class="center">{round(r['y'], 1)}</td>
        </tr>
        """

    report_date = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
    placement_count = len(rows)

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>As-Built Report - {project.name}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                color: #1f2937;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 40px 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                overflow: hidden;
            }}
            
            /* Header */
            .header {{
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                padding: 60px 40px;
                border-bottom: 5px solid #10b981;
            }}
            
            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 40px;
            }}
            
            .header-left {{
                flex: 1;
            }}
            
            .logo {{
                font-size: 28px;
                font-weight: 800;
                margin-bottom: 30px;
                letter-spacing: -1px;
            }}
            
            .logo-text {{
                background: white;
                color: #059669;
                padding: 4px 12px;
                border-radius: 6px;
                display: inline-block;
            }}
            
            .header h1 {{
                font-size: 42px;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .header p {{
                font-size: 16px;
                opacity: 0.95;
                margin-bottom: 8px;
            }}
            
            .report-type {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                margin-top: 15px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .header-meta {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .meta-row {{
                display: flex;
                justify-content: space-between;
                gap: 30px;
                font-size: 14px;
            }}
            
            .meta-item {{
                flex: 1;
            }}
            
            .meta-label {{
                opacity: 0.9;
                margin-bottom: 4px;
                font-weight: 600;
            }}
            
            .meta-value {{
                font-size: 16px;
                font-weight: 700;
            }}
            
            /* Main Content */
            .content {{
                padding: 50px 40px;
            }}
            
            .section {{
                margin-bottom: 50px;
            }}
            
            .section h2 {{
                font-size: 28px;
                color: #059669;
                margin-bottom: 25px;
                padding-bottom: 12px;
                border-bottom: 3px solid #d1fae5;
                font-weight: 700;
            }}
            
            .section-subtitle {{
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 20px;
                font-weight: 500;
            }}
            
            /* Floor Plan */
            .floor-plan-container {{
                background: #f9fafb;
                padding: 30px;
                border-radius: 8px;
                border: 2px solid #e5e7eb;
                margin-bottom: 30px;
            }}
            
            .floor-plan-container img {{
                max-width: 100%;
                height: auto;
                border-radius: 6px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                display: block;
            }}
            
            /* Summary Stats */
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                padding: 25px;
                border-radius: 8px;
                border-left: 5px solid #059669;
                box-shadow: 0 2px 8px rgba(5, 150, 105, 0.1);
            }}
            
            .stat-label {{
                font-size: 13px;
                color: #6b7280;
                margin-bottom: 8px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stat-value {{
                font-size: 32px;
                color: #059669;
                font-weight: 800;
            }}
            
            /* Placements Table */
            .table-wrapper {{
                overflow-x: auto;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                background: #f9fafb;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            
            thead {{
                background: linear-gradient(to right, #f3f4f6, #e5e7eb);
                border-bottom: 2px solid #d1d5db;
            }}
            
            th {{
                padding: 16px;
                text-align: left;
                font-weight: 700;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #374151;
                border-right: 1px solid #d1d5db;
            }}
            
            th:last-child {{
                border-right: none;
            }}
            
            td {{
                padding: 16px;
                border-bottom: 1px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                font-size: 14px;
            }}
            
            td:last-child {{
                border-right: none;
            }}
            
            tbody tr:hover {{
                background-color: #f9fafb;
            }}
            
            tbody tr:last-child td {{
                border-bottom: none;
            }}
            
            td.center {{
                text-align: center;
            }}
            
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .badge {{
                background-color: #dbeafe;
                color: #0284c7;
            }}
            
            .badge.manual {{
                background-color: #fef3c7;
                color: #92400e;
            }}
            
            .badge.gps {{
                background-color: #dbeafe;
                color: #0284c7;
            }}
            
            .badge.ai {{
                background-color: #e9d5ff;
                color: #6b21a8;
            }}
            
            /* Footer */
            .footer {{
                background: #f9fafb;
                padding: 30px 40px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 13px;
                text-align: center;
            }}
            
            .footer-content {{
                max-width: 600px;
                margin: 0 auto;
            }}
            
            .footer-divider {{
                margin: 20px 0;
                border-top: 1px solid #d1d5db;
            }}
            
            @media (max-width: 768px) {{
                .header-content {{
                    flex-direction: column;
                }}
                
                .header {{
                    padding: 40px 20px;
                }}
                
                .header h1 {{
                    font-size: 32px;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .meta-row {{
                    flex-direction: column;
                    gap: 15px;
                }}
                
                table {{
                    font-size: 12px;
                }}
                
                th, td {{
                    padding: 12px 8px;
                }}
                
                .summary {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                
                .container {{
                    box-shadow: none;
                    border-radius: 0;
                }}
                
                a {{
                    color: inherit;
                    text-decoration: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <div class="header-content">
                    <div class="header-left">
                        <div class="logo">
                            <span class="logo-text">SiteBuilt</span>
                        </div>
                        <h1>As-Built Report</h1>
                        <p>Professional Project Documentation</p>
                        <span class="report-type">GENERATED REPORT</span>
                    </div>
                    <div class="header-meta">
                        <div class="meta-row">
                            <div class="meta-item">
                                <div class="meta-label">Total Placements</div>
                                <div class="meta-value">{placement_count}</div>
                            </div>
                            <div class="meta-item">
                                <div class="meta-label">Generated</div>
                                <div class="meta-value">{report_date}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="content">
                <!-- Project Summary -->
                <section class="section">
                    <h2>Project Summary</h2>
                    <div class="summary">
                        <div class="stat-card">
                            <div class="stat-label">Project Name</div>
                            <div class="stat-value" style="font-size: 20px; text-align: left;">{project.name}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Total Placements</div>
                            <div class="stat-value">{placement_count}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Documentation Status</div>
                            <div class="stat-value" style="font-size: 20px; text-align: left;">Complete</div>
                        </div>
                    </div>
                    {f'<p class="section-subtitle">{project.description}</p>' if project.description else ''}
                </section>
                
                <!-- Floor Plan -->
                <section class="section">
                    <h2>Floor Plan</h2>
                    <p class="section-subtitle">Base Plan with Placement Coordinates</p>
                    <div class="floor-plan-container">
                        <img src="{plan.file_url}" alt="Floor Plan - {project.name}">
                    </div>
                </section>
                
                <!-- Photo Placements -->
                <section class="section">
                    <h2>Photo Placements</h2>
                    <p class="section-subtitle">Detailed record of all placed photographs and their locations</p>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Method</th>
                                    <th>Photo</th>
                                    <th>Timestamp / Location</th>
                                    <th>X Coord</th>
                                    <th>Y Coord</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_rows}
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-content">
                    <p><strong>SiteBuilt</strong> - Professional As-Built Documentation Platform</p>
                    <div class="footer-divider"></div>
                    <p>This report was generated by SiteBuilt on {report_date}. All coordinates and measurements are referenced to the floor plan shown above.</p>
                    <p style="margin-top: 10px; opacity: 0.7;">For questions or corrections, contact your project manager.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

