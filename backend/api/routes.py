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
    SearchQuery,
    SearchResponse,
    FrameResult,
    SegmentResult,
    BestFrame,
    VideoUploadResponse,
    VideoInfo,
    HealthResponse,
)
from core.video_processor import VideoProcessor
from core.feature_extractor import FeatureExtractor
from core.search_engine import SearchEngine
from core.segment_merger import SegmentMerger
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global servis instance'ları (app başlatıldığında initialize edilecek)
video_processor: Optional[VideoProcessor] = None
feature_extractor: Optional[FeatureExtractor] = None
search_engine: Optional[SearchEngine] = None
segment_merger: Optional[SegmentMerger] = None


def initialize_services():
    """
    Servisleri başlatır.

    Bu fonksiyon app başlatılırken çağrılmalıdır.
    """
    global video_processor, feature_extractor, search_engine, segment_merger

    logger.info("Initializing services...")

    video_processor = VideoProcessor()
    feature_extractor = FeatureExtractor()
    search_engine = SearchEngine()
    segment_merger = SegmentMerger(merge_threshold=0.0)

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
        original_filename = file.filename
        logger.info(f"Received video upload: {original_filename}")

        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            # Upload edilen dosyayı geçici dosyaya kopyala
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)

        # Video'yu işle
        video_id, frame_metadata_list, video_metadata = video_processor.process_video(
            tmp_path, original_filename
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
async def search(request: SearchQuery):
    query = request.query
    video_id = request.video_id
    k = request.k
    similarity_threshold = request.similarity_threshold
    merge_segments = request.merge_segments
    """
    Arama endpoint.

    Metin sorgusuyla benzer frame'leri bulur ve isteğe bağlı olarak
    çakışan segmentleri birleştirir.
    """
    try:
        logger.info(
            f"Search query: '{query}', video_id={video_id}, k={k}, "
            f"merge_segments={merge_segments}"
        )

        if not search_engine.index:
            raise HTTPException(
                status_code=400,
                detail="No videos indexed. Please upload a video first.",
            )

        if video_id:
            if not search_engine.get_video_metadata(video_id):
                raise HTTPException(
                    status_code=404, detail=f"Video '{video_id}' not found."
                )

        # Text feature çıkar
        text_features = feature_extractor.extract_text_features(query)

        search_results = search_engine.search(
            text_features,
            k=k,
            similarity_threshold=similarity_threshold,
            video_id=video_id,
        )

        # Frame sonuçlarını oluştur
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

        # Response oluştur
        response_data = {
            "query": query,
            "video_id": video_id,
            "results": frame_results,
            "total_results": len(frame_results),
        }

        # Segment birleştirme işlemi
        if merge_segments and search_results:
            logger.info("Merging overlapping segments...")

            # Segmentleri birleştir
            merged_segments = segment_merger.merge_search_results(
                search_results,
                segment_duration=10.0,  # Her frame için ±5 saniye segment
            )

            # Segment sonuçlarını oluştur
            segment_results = []
            for segment in merged_segments:
                segment_results.append(
                    SegmentResult(
                        video_id=segment.video_id,
                        video_url=f"/videos/{segment.video_id}",
                        start_time=segment.start_time,
                        end_time=segment.end_time,
                        duration=round(segment.end_time - segment.start_time, 2),
                        best_score=segment.best_score,
                        best_frame=BestFrame(**segment.best_frame),
                        frame_count=segment.frame_count,
                    )
                )

            # Özet bilgi
            merge_info = segment_merger.get_segment_summary(merged_segments)

            response_data["segments"] = segment_results
            response_data["merge_info"] = merge_info

            logger.info(
                f"Segment merge completed: {len(segment_results)} segments "
                f"created from {len(frame_results)} frames"
            )

        return SearchResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
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
