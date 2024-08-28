import logging

from pydantic import ValidationError
from quart import Quart, ResponseReturnValue
from quart_schema import Info, QuartSchema, RequestSchemaValidationError, Tag
from sqlalchemy import select

from chat_service.config import settings
from chat_service.model import async_session
from chat_service.routes import bp

logger = logging.getLogger(__name__)


def create_app() -> Quart:
    app = Quart(__name__)

    # setup quart schema to provide API documentation
    QuartSchema(
        app,
        info=Info(title="Chat Service", version="0.0.1"),
        openapi_path=f"{settings.base_path}/openapi.json",
        swagger_ui_path=f"{settings.base_path}/docs",
        redoc_ui_path=f"{settings.base_path}/redocs",
        tags=[
            Tag(
                name="Messages",
                description="Endpoints for submitting and retrieving messages for a chat session.",
            ),
        ],
        convert_casing=False,
    )

    app.config.from_object(settings.quart)

    app.register_blueprint(blueprint=bp, url_prefix=f"{settings.base_path}")

    @app.errorhandler(RequestSchemaValidationError)
    async def handle_request_validation_error(
        e: RequestSchemaValidationError,
    ) -> ResponseReturnValue:
        """Global error handler for request schema validation errors."""
        logger.info("Validation error for request", exc_info=e)
        if isinstance(e.validation_error, ValidationError):
            return {"error": e.validation_error.errors()}, 400
        else:
            return {"error": str(e.validation_error)}, 400

    @app.route("/health")
    async def health_check() -> ResponseReturnValue:
        """Health check endpoint"""
        async with async_session() as session:
            await session.execute(select(1))
        return "Healthy"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
