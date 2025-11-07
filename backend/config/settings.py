"""
Bu modül projenin tüm konfigürasyon ayarlarını merkezi olarak yönetir.
Ortam değişkenleri ve varsayılan değerler burada tanımlanır.
"""

from pathlib import Path
from typing import Optional
import os


class Settings:
    """
    Uygulama ayarları sınıfı.

    Attributes:
        PROJECT_ROOT: Proje kök dizini
        UPLOAD_DIR: Yüklenen videoların saklanacağı dizin
        FRAME_EXTRACTION_DIR: Çıkarılan frame'lerin saklanacağı dizin
        FAISS_INDEX_PATH: FAISS index dosya yolu
        METADATA_PATH: Video metadata dosya yolu
        DEVICE: İşlem için kullanılacak cihaz (cpu/cuda)
        MODEL_NAME: Kullanılacak CLIP model ismi
        FRAMES_PER_SECOND: Saniyede kaç frame çıkarılacağı
        MAX_VIDEO_SIZE_MB: Maksimum video boyutu (MB)
        ALLOWED_VIDEO_FORMATS: İzin verilen video formatları
    """

    # Dizin yapılandırması
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = PROJECT_ROOT / "uploads"
    FRAME_EXTRACTION_DIR: Path = PROJECT_ROOT / "frames"

    # Index ve metadata yolları
    FAISS_INDEX_PATH: str = "video_faiss.index"
    METADATA_PATH: str = "video_metadata.npy"

    # Model ayarları
    DEVICE: Optional[str] = os.getenv("DEVICE", "cpu")
    MODEL_NAME: str = "openai/clip-vit-base-patch32"

    # Video işleme ayarları
    FRAMES_PER_SECOND: int = 1  # Her saniyeden 1 frame çıkar
    MAX_VIDEO_SIZE_MB: int = 500  # Maksimum 500MB
    ALLOWED_VIDEO_FORMATS: set = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

    # API ayarları
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list = ["*"]

    # Arama ayarları
    DEFAULT_TOP_K: int = 30
    MIN_SIMILARITY_THRESHOLD: float = 0.1

    # Video oynatma ayarları (saniye cinsinden)
    VIDEO_PLAYBACK_OFFSET: int = 5  # Bulunan frame'den ±5 saniye

    @classmethod
    def create_directories(cls) -> None:
        """
        Gerekli dizinleri oluşturur.

        Uygulama başlarken upload ve frame extraction dizinlerini oluşturur.
        """
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.FRAME_EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_frame_dir(cls, video_id: str) -> Path:
        """
        Belirli bir video için frame dizinini döndürür.

        Args:
            video_id: Video benzersiz ID'si

        Returns:
            Video frame'lerinin saklandığı dizin yolu
        """
        frame_dir = cls.FRAME_EXTRACTION_DIR / video_id
        frame_dir.mkdir(parents=True, exist_ok=True)
        return frame_dir


settings = Settings()
