import logging
from typing import Any

from app.modules.attendance.service import AttendanceService

logger = logging.getLogger(__name__)


class AttendanceAnalyzer:
    """Coordinator for Attendance & Leave domain analysis."""

    def __init__(self, service: AttendanceService):
        self.service = service

    def run_analysis(self) -> dict[str, Any]:
        logger.info("Executing Attendance & Leave domain analysis...")
        overview = self.service.get_attendance_overview()
        leave_overview = self.service.get_leave_overview()
        quality = self.service.get_attendance_quality()

        return {
            "status": "COMPLETED",
            "overview": overview.model_dump(),
            "leave_overview": leave_overview.model_dump(),
            "quality": quality.model_dump(),
        }
