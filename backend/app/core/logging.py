import logging
import sys

logger = logging.getLogger("airis_insights")


def setup_logging(level: str = "INFO") -> None:
    """Configures application-wide logging format."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def log_event(event_name: str, level: int = logging.INFO, **context) -> None:
    """
    Emits a structured log event with contextual metadata.
    Avoids logging raw data rows for privacy and compliance.
    """
    ctx_str = " ".join(f"{k}={v}" for k, v in context.items() if v is not None)
    msg = f"{event_name} {ctx_str}".strip()
    logger.log(level, msg, extra=context)
