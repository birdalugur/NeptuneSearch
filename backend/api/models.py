from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    """Arama sorgusu modeli"""

    query: str = Field(..., min_length=1, description="Arama sorgusu metni")
    video_id: Optional[str] = Field(
        None, description="Arama yapılacak video ID (opsiyonel)"
    )
    k: Optional[int] = Field(30, ge=1, le=100, description="Maksimum sonuç sayısı")
    similarity_threshold: Optional[float] = Field(
        0.1, ge=0.0, le=1.0, description="Minimum benzerlik eşiği"
    )
    merge_segments: Optional[bool] = Field(
        True, description="Çakışan segmentleri birleştir"
    )


class FrameResult(BaseModel):
    """Tek bir frame sonucu"""

    frame_id: str
    video_id: str
    timestamp: float
    score: float
    rank: int
    thumbnail_url: str


class BestFrame(BaseModel):
    """Segment içindeki en iyi frame bilgisi"""

    frame_id: str
    timestamp: float
    rank: int
    thumbnail_url: str


class SegmentResult(BaseModel):
    """Birleştirilmiş video segment sonucu"""

    video_id: str
    video_url: str
    start_time: float
    end_time: float
    duration: float = Field(..., description="Segment süresi (saniye)")
    best_score: float
    best_frame: BestFrame
    frame_count: int = Field(..., description="Segment içindeki frame sayısı")


class VideoInfo(BaseModel):
    """Video bilgisi modeli"""

    video_id: str
    original_filename: str
    duration: float
    fps: float
    width: int
    height: int
    total_frames: int


class SearchResponse(BaseModel):
    """Arama sonucu response modeli"""

    query: str
    video_id: Optional[str] = None
    results: List[FrameResult]
    total_results: int
    segments: Optional[List[SegmentResult]] = Field(
        None, description="Birleştirilmiş segment sonuçları (opsiyonel)"
    )
    merge_info: Optional[dict] = Field(
        None, description="Birleştirme istatistikleri (opsiyonel)"
    )


class VideoUploadResponse(BaseModel):
    """Video upload response modeli"""

    success: bool
    message: str
    video_id: Optional[str] = None
    video_info: Optional[VideoInfo] = None
    frames_extracted: Optional[int] = None


# class VideoSegmentRequest(BaseModel):
#     """Video segment request modeli"""

#     video_id: str
#     timestamp: float


# class VideoSegmentResponse(BaseModel):
#     """Video segment response modeli"""

#     video_id: str
#     video_url: str
#     start_time: float
#     end_time: float
#     duration: float
#     center_timestamp: float


class ErrorResponse(BaseModel):
    """Hata response modeli"""

    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response modeli"""

    status: str
    videos_indexed: int
    frames_indexed: int
