from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    """Arama sorgusu modeli"""

    query: str = Field(..., min_length=1, description="Arama sorgusu metni")
    k: Optional[int] = Field(30, ge=1, le=100, description="Maksimum sonuç sayısı")
    similarity_threshold: Optional[float] = Field(
        0.1, ge=0.0, le=1.0, description="Minimum benzerlik eşiği"
    )


class FrameResult(BaseModel):
    """Tek bir frame sonucu"""

    frame_id: str
    video_id: str
    timestamp: float
    score: float
    rank: int
    thumbnail_url: str


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
    results: List[FrameResult]
    total_results: int


class VideoUploadResponse(BaseModel):
    """Video upload response modeli"""

    success: bool
    message: str
    video_id: Optional[str] = None
    video_info: Optional[VideoInfo] = None
    frames_extracted: Optional[int] = None


class VideoSegmentRequest(BaseModel):
    """Video segment request modeli"""

    video_id: str
    timestamp: float


class VideoSegmentResponse(BaseModel):
    """Video segment response modeli"""

    video_id: str
    video_url: str
    start_time: float
    end_time: float
    duration: float
    center_timestamp: float


class ErrorResponse(BaseModel):
    """Hata response modeli"""

    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response modeli"""

    status: str
    videos_indexed: int
    frames_indexed: int
