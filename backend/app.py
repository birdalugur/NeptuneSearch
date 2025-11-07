"""
Ana Uygulama Giriş Noktası

Bu modül FastAPI uygulamasını başlatır ve tüm route'ları yapılandırır.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routes import router, initialize_services
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    FastAPI uygulamasını oluşturur ve yapılandırır.

    Returns:
        Yapılandırılmış FastAPI instance'ı
    """

    app = FastAPI(
        title="Video Semantic Search API",
        description="Video içeriğinde semantik arama yapan AI destekli API",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings.create_directories()

    # Static file serving için frame'leri mount et
    if settings.FRAME_EXTRACTION_DIR.exists():
        app.mount(
            "/frames",
            StaticFiles(directory=settings.FRAME_EXTRACTION_DIR),
            name="frames",
        )

    app.include_router(router, prefix="/api")

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Uygulama başlarken çalışır"""
        logger.info("Starting Video Semantic Search API...")
        initialize_services()
        logger.info("Application started successfully")

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Uygulama kapanırken çalışır"""
        logger.info("Shutting down Video Semantic Search API...")

    return app


app = create_app()


if __name__ == "__main__":
    """
    Uygulamayı başlatır.
    
    Komut satırından direkt çalıştırıldığında uvicorn server'ı başlatır.
    
    Kullanım:
        python app.py
    """
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
