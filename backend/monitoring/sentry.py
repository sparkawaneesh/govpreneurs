import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
import logging

logger = logging.getLogger(__name__)

def init_sentry():
    """
    Initializes Sentry for error tracking.
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logger.warning("SENTRY_DSN not found. Sentry monitoring is disabled.")
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=os.getenv("ENVIRONMENT", "development")
    )
    logger.info("Sentry monitoring initialized successfully.")
