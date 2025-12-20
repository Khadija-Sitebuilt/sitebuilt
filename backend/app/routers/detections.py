from fastapi import APIRouter
from uuid import UUID

router = APIRouter(
    prefix="/photos/{photo_id}",
    tags=["detections"],
)

@router.get("/detections")
def get_detections(photo_id: UUID):
    # 🔴 DEMO ONLY – FAKE DATA
    return {
        "photo_id": photo_id,
        "detections": [
            {
                "label": "pipe",
                "confidence": 0.87,
                "bbox": [120, 200, 80, 40],
            },
            {
                "label": "valve",
                "confidence": 0.74,
                "bbox": [300, 180, 60, 60],
            },
        ],
        "note": "Demo-only stub detection",
    }
