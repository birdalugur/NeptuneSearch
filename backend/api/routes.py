"""
Bu modül tüm FastAPI endpoint'lerini tanımlar.
Video upload, arama ve video segment servisleri sağlar.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
import tempfile
import shutil

from api.models import (
    SearchResponse,
    FrameResult,
    VideoUploadResponse,
    VideoInfo,
    VideoSegmentRequest,
    VideoSegmentResponse,
    HealthResponse,
)
from core.video_processor import VideoProcessor
from core.feature_extractor import FeatureExtractor
from core.search_engine import SearchEngine
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global servis instance'ları (app başlatıldığında initialize edilecek)
video_processor: Optional[VideoProcessor] = None
feature_extractor: Optional[FeatureExtractor] = None
search_engine: Optional[SearchEngine] = None


def initialize_services():
    """
    Servisleri başlatır.

    Bu fonksiyon app başlatılırken çağrılmalıdır.
    """
    global video_processor, feature_extractor, search_engine

    logger.info("Initializing services...")

    video_processor = VideoProcessor()
    feature_extractor = FeatureExtractor()
    search_engine = SearchEngine()

    search_engine.load_index()

    logger.info("Services initialized successfully")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Servisin çalışır durumda olduğunu kontrol eder.
    """
    videos = search_engine.get_all_videos() if search_engine else []
    frames = len(search_engine.frame_metadata_list) if search_engine else 0

    return HealthResponse(
        status="healthy", videos_indexed=len(videos), frames_indexed=frames
    )


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Video upload endpoint.

    Video dosyasını yükler, frame'leri çıkarır ve index'e ekler.
    """
    try:
        logger.info(f"Received video upload: {file.filename}")

        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            # Upload edilen dosyayı geçici dosyaya kopyala
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)

        # Video'yu işle
        video_id, frame_metadata_list, video_metadata = video_processor.process_video(
            tmp_path
        )

        # Frame'lerden feature'ları çıkar
        frame_paths = [Path(fm.frame_path) for fm in frame_metadata_list]
        features = feature_extractor.extract_image_features(frame_paths)

        # Index'e ekle
        search_engine.build_index(features, frame_metadata_list, video_metadata)

        # Index'i kaydet
        search_engine.save_index()

        logger.info(f"Video processed successfully: {video_id}")

        return VideoUploadResponse(
            success=True,
            message="Video uploaded and processed successfully",
            video_id=video_id,
            video_info=VideoInfo(
                video_id=video_metadata.video_id,
                original_filename=video_metadata.original_filename,
                duration=video_metadata.duration,
                fps=video_metadata.fps,
                width=video_metadata.width,
                height=video_metadata.height,
                total_frames=video_metadata.total_frames,
            ),
            frames_extracted=len(frame_metadata_list),
        )

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(
    query: str = Form(...),
    video_id: Optional[str] = Form(None),
    k: int = Form(30),
    similarity_threshold: float = Form(0.1),
):
    """
    Arama endpoint.

    Metin sorgusuyla benzer frame'leri bulur.
    """
    try:
        logger.info(f"Search query: '{query}', video_id={video_id}, k={k}")

        if not search_engine.index:
            raise HTTPException(
                status_code=400,
                detail="No videos indexed. Please upload a video first.",
            )

        if video_id:
            video_metadata = search_engine.get_video_metadata(video_id)
            if not video_metadata:
                raise HTTPException(
                    status_code=404, detail=f"Video with id '{video_id}' not found."
                )

        # Text feature çıkar
        text_features = feature_extractor.extract_text_features(query)

        search_results = search_engine.search(
            text_features,
            k=k,
            similarity_threshold=similarity_threshold,
            video_id=video_id,
        )

        # Response oluştur
        frame_results = []
        for result in search_results:
            frame_metadata = result["frame_metadata"]

            # Thumbnail URL oluştur
            thumbnail_url = f"/frames/{frame_metadata.video_id}/{Path(frame_metadata.frame_path).name}"

            frame_results.append(
                FrameResult(
                    frame_id=frame_metadata.frame_id,
                    video_id=frame_metadata.video_id,
                    timestamp=frame_metadata.timestamp,
                    score=result["score"],
                    rank=result["rank"],
                    thumbnail_url=thumbnail_url,
                )
            )

        return SearchResponse(
            query=query,
            video_id=video_id,
            results=frame_results,
            total_results=len(frame_results),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video-segment", response_model=VideoSegmentResponse)
async def get_video_segment(request: VideoSegmentRequest):
    """
    Video segment bilgisi endpoint.

    Belirli bir timestamp için video segment bilgilerini döndürür.
    """
    try:
        # Video metadata'sını al
        video_metadata = search_engine.get_video_metadata(request.video_id)

        if not video_metadata:
            raise HTTPException(status_code=404, detail="Video not found")

        # Segment bilgilerini hesapla
        segment_info = video_processor.get_video_segment_info(
            request.timestamp, video_metadata
        )

        # Video URL oluştur
        video_url = f"/videos/{request.video_id}"
        return VideoSegmentResponse(
            video_id=request.video_id,
            video_url=video_url,
            start_time=segment_info["start_time"],
            end_time=segment_info["end_time"],
            duration=segment_info["duration"],
            center_timestamp=segment_info["center_timestamp"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video segment error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """
    Video dosyası endpoint.

    Video dosyasını stream olarak döndürür.
    """
    try:
        # Video metadata'sını al
        video_metadata = search_engine.get_video_metadata(video_id)
        if not video_metadata:
            raise HTTPException(status_code=404, detail="Video not found")

        video_path = Path(video_metadata.video_path)

        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")

        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=video_metadata.original_filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video file error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos")
async def list_videos():
    """
    Video listesi endpoint.

    Tüm indexed videoları listeler.
    """
    try:
        videos = search_engine.get_all_videos()

        video_list = [
            VideoInfo(
                video_id=v.video_id,
                original_filename=v.original_filename,
                duration=v.duration,
                fps=v.fps,
                width=v.width,
                height=v.height,
                total_frames=v.total_frames,
            )
            for v in videos
        ]

        return {"videos": video_list, "total": len(video_list)}

    except Exception as e:
        logger.error(f"List videos error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
