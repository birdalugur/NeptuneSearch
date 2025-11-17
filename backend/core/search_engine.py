"""
Bu modül FAISS tabanlı benzerlik araması yapar.
Feature vektörlerini indeksler ve hızlı arama sağlar.
"""

from pathlib import Path
from typing import List, Optional, Dict
import numpy as np
import faiss
import pickle

from config.settings import settings
from utils.logger import get_logger
from core.video_processor import FrameMetadata, VideoMetadata

logger = get_logger(__name__)


class SearchEngine:
    """
    FAISS tabanlı arama motoru sınıfı.

    Feature vektörlerini indeksler ve benzerlik araması yapar.
    """

    def __init__(
        self, index_path: Optional[str] = None, metadata_path: Optional[str] = None
    ):
        """
        SearchEngine instance'ı oluşturur.

        Args:
            index_path: FAISS index dosya yolu
            metadata_path: Metadata dosya yolu
        """
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.metadata_path = metadata_path or settings.METADATA_PATH

        self.index: Optional[faiss.Index] = None
        self.frame_metadata_list: List[FrameMetadata] = []
        self.video_metadata_dict: Dict[str, VideoMetadata] = {}

        logger.info("SearchEngine initialized")

    def build_index(
        self,
        features: np.ndarray,
        frame_metadata_list: List[FrameMetadata],
        video_metadata: VideoMetadata,
    ) -> None:
        """
        Feature vektörlerinden FAISS index oluşturur.

        Args:
            features: Feature vektörleri (N, dim)
            frame_metadata_list: Frame metadata listesi
            video_metadata: Video metadata
        """
        logger.info(f"Building FAISS index with {len(features)} vectors")

        if len(features) != len(frame_metadata_list):
            raise ValueError(
                f"Features count ({len(features)}) doesn't match "
                f"metadata count ({len(frame_metadata_list)})"
            )

        # L2 normalizasyonu (cosine similarity için)
        faiss.normalize_L2(features)

        # FAISS index oluştur (Inner Product = Cosine Similarity normalized vektörler için)
        embedding_dim = features.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatIP(embedding_dim)
            logger.info(f"Created new FAISS index with dimension {embedding_dim}")

        self.index.add(features)

        self.frame_metadata_list.extend(frame_metadata_list)
        self.video_metadata_dict[video_metadata.video_id] = video_metadata

        logger.info(f"Index built successfully. Total vectors: {self.index.ntotal}")

    def save_index(self) -> None:
        """
        Index ve metadata'yı diske kaydeder.
        """
        if self.index is None:
            logger.warning("No index to save")
            return

        logger.info(f"Saving index to {self.index_path}")

        faiss.write_index(self.index, self.index_path)

        metadata = {
            "frame_metadata_list": self.frame_metadata_list,
            "video_metadata_dict": self.video_metadata_dict,
        }

        with open(self.metadata_path, "wb") as f:
            pickle.dump(metadata, f)

        logger.info(
            f"Index and metadata saved successfully. "
            f"Total frames: {len(self.frame_metadata_list)}, "
            f"Videos: {len(self.video_metadata_dict)}"
        )

    def load_index(self) -> bool:
        """
        Kaydedilmiş index ve metadata'yı yükler.

        Returns:
            Yükleme başarılıysa True, değilse False
        """
        if not Path(self.index_path).exists() or not Path(self.metadata_path).exists():
            logger.warning("Index or metadata file not found")
            return False

        logger.info("Loading existing index and metadata")

        try:
            self.index = faiss.read_index(self.index_path)

            with open(self.metadata_path, "rb") as f:
                metadata = pickle.load(f)

            self.frame_metadata_list = metadata["frame_metadata_list"]
            self.video_metadata_dict = metadata["video_metadata_dict"]

            logger.info(
                f"Index loaded successfully. "
                f"Total frames: {len(self.frame_metadata_list)}, "
                f"Videos: {len(self.video_metadata_dict)}"
            )

            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def search(
        self,
        query_features: np.ndarray,
        k: int = None,
        similarity_threshold: float = None,
        video_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Query feature'ına en benzer frame'leri bulur.

        Args:
            query_features: Query feature vektörü
            k: Döndürülecek maksimum sonuç sayısı
            similarity_threshold: Minimum benzerlik eşiği
            video_id: Belirli bir video ID (opsiyonel, belirtilmezse tüm videolarda arar)

        Returns:
            Sonuç listesi (her biri frame_metadata, video_metadata ve score içerir)
        """
        if self.index is None:
            raise RuntimeError("Index is not loaded or built")

        k = k or settings.DEFAULT_TOP_K
        similarity_threshold = similarity_threshold or settings.MIN_SIMILARITY_THRESHOLD

        # Query feature'ı normalize et
        query_features = query_features.reshape(1, -1).astype("float32")
        faiss.normalize_L2(query_features)

        # Eğer video_id belirtilmişse, filtreleme sonrası k'dan az sonuç kalabilir
        search_k = k * 10 if video_id else k

        scores, indices = self.index.search(
            query_features, min(search_k, self.index.ntotal)
        )

        results = []
        for idx, (index, score) in enumerate(zip(indices[0], scores[0])):
            if index == -1 or score < similarity_threshold:
                continue

            frame_metadata = self.frame_metadata_list[index]

            # Eğer video_id belirtilmişse, sadece o video'nun frame'lerini al
            if video_id and frame_metadata.video_id != video_id:
                continue

            video_metadata = self.video_metadata_dict[frame_metadata.video_id]

            results.append(
                {
                    "rank": len(results) + 1,  # Filtrelemeden sonra yeniden rank
                    "score": float(score),
                    "frame_metadata": frame_metadata,
                    "video_metadata": video_metadata,
                }
            )

            # İstenen sonuç sayısına ulaşıldıysa dur
            if len(results) >= k:
                break

        if video_id:
            logger.info(
                f"Search completed for video {video_id}: {len(results)} results found"
            )
        else:
            logger.info(
                f"Search completed across all videos: {len(results)} results found"
            )

        return results

    def get_video_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        """
        Video ID'sine göre video metadata'sını döndürür.

        Args:
            video_id: Video ID

        Returns:
            VideoMetadata veya None
        """
        return self.video_metadata_dict.get(video_id)

    def get_all_videos(self) -> List[VideoMetadata]:
        """
        Tüm video metadata'larını döndürür.

        Returns:
            VideoMetadata listesi
        """
        return list(self.video_metadata_dict.values())

    def clear_index(self) -> None:
        """
        Index ve metadata'yı temizler.
        """
        self.index = None
        self.frame_metadata_list = []
        self.video_metadata_dict = {}

        logger.info("Index and metadata cleared")

    def remove_video(self, video_id: str) -> bool:
        """
        Belirli bir video'nun verilerini index'ten kaldırır.

        Not: Bu işlem index'i yeniden oluşturmayı gerektirir.

        Args:
            video_id: Kaldırılacak video ID'si

        Returns:
            İşlem başarılıysa True
        """
        if video_id not in self.video_metadata_dict:
            logger.warning(f"Video {video_id} not found in index")
            return False

        logger.info(f"Removing video {video_id} from index")

        # Bu video'ya ait olmayan frame'leri filtrele
        new_frame_metadata_list = [
            fm for fm in self.frame_metadata_list if fm.video_id != video_id
        ]

        removed_count = len(self.frame_metadata_list) - len(new_frame_metadata_list)

        # Video metadata'sını kaldır
        del self.video_metadata_dict[video_id]

        # Yeni metadata listesini kaydet
        self.frame_metadata_list = new_frame_metadata_list

        # Index'i yeniden oluşturulması gerekecek
        self.index = None

        logger.info(
            f"Removed {removed_count} frames from video {video_id}. "
            "Index needs to be rebuilt."
        )

        return True
