"""
Bu modül video dosyalarını işler, frame'leri çıkarır ve metadata yönetimi yapar.
OpenCV kullanarak video işleme operasyonlarını gerçekleştirir.
"""

import cv2
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FrameMetadata:
    """
    Frame metadata bilgilerini tutan veri sınıfı.

    Attributes:
        frame_id: Frame benzersiz ID'si
        video_id: Ait olduğu video ID'si
        frame_path: Frame dosya yolu
        timestamp: Videodaki zaman damgası (saniye)
        frame_number: Frame numarası
    """

    frame_id: str
    video_id: str
    frame_path: str
    timestamp: float
    frame_number: int


@dataclass
class VideoMetadata:
    """
    Video metadata bilgilerini tutan veri sınıfı.

    Attributes:
        video_id: Video benzersiz ID'si
        original_filename: Orijinal dosya adı
        video_path: Video dosya yolu
        duration: Video süresi (saniye)
        fps: Video FPS değeri
        total_frames: Toplam frame sayısı
        width: Video genişliği
        height: Video yüksekliği
    """

    video_id: str
    original_filename: str
    video_path: str
    duration: float
    fps: float
    total_frames: int
    width: int
    height: int


class VideoProcessor:
    """
    Video işleme sınıfı.

    Video yükleme, frame çıkarma ve metadata yönetimi işlemlerini gerçekleştirir.
    """

    def __init__(self):
        """VideoProcessor instance'ı oluşturur."""
        self.frames_per_second = settings.FRAMES_PER_SECOND
        logger.info(
            f"VideoProcessor initialized with {self.frames_per_second} FPS extraction rate"
        )

    def validate_video(self, file_path: Path) -> bool:
        """
        Video dosyasını doğrular.

        Args:
            file_path: Video dosya yolu

        Returns:
            Video geçerliyse True, değilse False
        """

        if file_path.suffix.lower() not in settings.ALLOWED_VIDEO_FORMATS:
            logger.warning(f"Invalid video format: {file_path.suffix}")
            return False

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.MAX_VIDEO_SIZE_MB:
            logger.warning(f"Video too large: {file_size_mb:.2f}MB")
            return False

        cap = cv2.VideoCapture(str(file_path))
        is_valid = cap.isOpened()
        cap.release()

        return is_valid

    def get_video_info(self, video_path: Path) -> Optional[Dict]:
        """
        Video hakkında temel bilgileri döndürür.

        Args:
            video_path: Video dosya yolu

        Returns:
            Video bilgileri dictionary veya None
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        cap.release()

        return {
            "fps": fps,
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration": duration,
        }

    def extract_frames(
        self, video_path: Path, video_id: str, original_filename: str
    ) -> Tuple[List[FrameMetadata], VideoMetadata]:
        """
        Videodan frame'leri çıkarır ve metadata oluşturur.

        Args:
            video_path: Video dosya yolu
            video_id: Video benzersiz ID'si
            original_filename: Orijinal dosya adı

        Returns:
            (frame_metadata_listesi, video_metadata) tuple'ı
        """
        logger.info(f"Starting frame extraction from {video_path}")

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        video_metadata = VideoMetadata(
            video_id=video_id,
            original_filename=original_filename,
            video_path=str(video_path),
            duration=duration,
            fps=fps,
            total_frames=total_frames,
            width=width,
            height=height,
        )

        frame_interval = int(fps / self.frames_per_second) if fps > 0 else 1
        frame_metadata_list: List[FrameMetadata] = []
        frame_dir = settings.get_frame_dir(video_id)

        frame_count = 0
        extracted_count = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_id = f"{video_id}_frame_{extracted_count:06d}"
                frame_filename = f"{frame_id}.jpg"
                frame_path = frame_dir / frame_filename

                cv2.imwrite(str(frame_path), frame)

                timestamp = frame_count / fps if fps > 0 else frame_count

                metadata = FrameMetadata(
                    frame_id=frame_id,
                    video_id=video_id,
                    frame_path=str(frame_path),
                    timestamp=timestamp,
                    frame_number=frame_count,
                )

                frame_metadata_list.append(metadata)
                extracted_count += 1

                if extracted_count % 100 == 0:
                    logger.info(f"Extracted {extracted_count} frames...")

            frame_count += 1

        cap.release()

        logger.info(
            f"Frame extraction completed: {extracted_count} frames "
            f"extracted from {total_frames} total frames"
        )

        return frame_metadata_list, video_metadata

    def process_video(
        self, video_file_path: Path, original_filename: str
    ) -> Tuple[str, List[FrameMetadata], VideoMetadata]:
        """
        Video'yu işler: doğrular, frame çıkarır ve metadata oluşturur.

        Args:
            video_file_path: Video dosya yolu (geçici dosya)
            original_filename: Orijinal dosya adı

        Returns:
            (video_id, frame_metadata_list, video_metadata) tuple'ı

        Raises:
            ValueError: Video geçersizse
        """
        if not self.validate_video(video_file_path):
            raise ValueError("Invalid video file")

        video_id = str(uuid.uuid4())

        permanent_path = settings.UPLOAD_DIR / f"{video_id}{video_file_path.suffix}"
        video_file_path.rename(permanent_path)

        frame_metadata_list, video_metadata = self.extract_frames(
            permanent_path, video_id, original_filename
        )

        return video_id, frame_metadata_list, video_metadata

