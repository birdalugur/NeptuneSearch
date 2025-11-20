"""
Video segment birleştirme modülü.

Arama sonuçlarında çakışan segmentleri tespit eder ve birleştirir.
"""

from typing import List, Dict
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoSegment:
    """
    Birleştirilmiş video segmenti.

    Attributes:
        video_id: Video benzersiz ID'si
        start_time: Segment başlangıç zamanı (saniye)
        end_time: Segment bitiş zamanı (saniye)
        best_score: Segmentteki en yüksek benzerlik skoru
        best_frame: En yüksek skora sahip frame bilgisi
        frame_count: Segment içindeki toplam frame sayısı
    """

    video_id: str
    start_time: float
    end_time: float
    best_score: float
    best_frame: Dict
    frame_count: int


class SegmentMerger:
    """
    Video segmentlerini birleştiren sınıf.

    Aynı videodan gelen çakışan segmentleri tespit eder ve
    akıllı birleştirme algoritması ile tek segment haline getirir.
    """

    def __init__(self, merge_threshold: float = 0.0):
        """
        SegmentMerger instance'ı oluşturur.

        Args:
            merge_threshold: Segmentler arası maksimum boşluk süresi (saniye).
                           Bu değer kadar veya daha az boşluk varsa segmentler birleştirilir.
        """
        self.merge_threshold = merge_threshold
        logger.info(f"SegmentMerger initialized with threshold: {merge_threshold}s")

    def merge_search_results(
        self, search_results: List[Dict], segment_duration: float = 10.0
    ) -> List[VideoSegment]:
        """
        Arama sonuçlarını video segmentlerine dönüştürür ve birleştirir.

        Args:
            search_results: Search engine'den dönen sonuç listesi
            segment_duration: Her frame için oluşturulacak segment süresi (saniye)

        Returns:
            Birleştirilmiş VideoSegment listesi
        """
        if not search_results:
            return []

        logger.info(f"Merging {len(search_results)} search results")

        # 1. Video ID'ye göre gruplama
        grouped_by_video = self._group_by_video(search_results)

        all_segments = []

        # 2. Her video için ayrı ayrı birleştirme
        for video_id, frames in grouped_by_video.items():
            logger.debug(f"Processing {len(frames)} frames for video {video_id}")

            # Frame'leri timestamp'e göre sırala
            sorted_frames = sorted(frames, key=lambda x: x["frame_metadata"].timestamp)

            # Her frame için segment oluştur
            frame_segments = []
            for frame in sorted_frames:
                timestamp = frame["frame_metadata"].timestamp
                half_duration = segment_duration / 2.0

                segment = {
                    "video_id": video_id,
                    "start_time": max(0, timestamp - half_duration),
                    "end_time": timestamp + half_duration,
                    "score": frame["score"],
                    "frame": frame,
                }
                frame_segments.append(segment)

            # Segmentleri birleştir
            merged = self._merge_intervals(frame_segments)
            all_segments.extend(merged)

        # Tüm segmentleri skora göre sırala
        all_segments.sort(key=lambda x: x.best_score, reverse=True)

        logger.info(
            f"Merge completed: {len(all_segments)} segments created from {len(search_results)} frames"
        )

        return all_segments

    def _group_by_video(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Sonuçları video ID'sine göre gruplar.

        Args:
            results: Arama sonuçları listesi

        Returns:
            Video ID'ye göre gruplanmış dictionary
        """
        grouped = {}

        for result in results:
            video_id = result["frame_metadata"].video_id
            if video_id not in grouped:
                grouped[video_id] = []
            grouped[video_id].append(result)

        return grouped

    def _merge_intervals(self, segments: List[Dict]) -> List[VideoSegment]:
        """
        Çakışan veya bitişik segmentleri birleştirir.

        Interval Merging Algorithm kullanır:
        - Segmentler zaten start_time'a göre sıralı gelir
        - Eğer mevcut segment, önceki segmentin bitiş zamanıyla çakışıyorsa birleştirilir
        - Birleştirme sırasında en yüksek skora sahip frame korunur

        Args:
            segments: Sıralanmış segment listesi

        Returns:
            Birleştirilmiş VideoSegment listesi
        """
        if not segments:
            return []

        merged = []
        current = segments[0].copy()
        current["frames"] = [current["frame"]]

        for i in range(1, len(segments)):
            next_segment = segments[i]

            # Çakışma kontrolü: mevcut segment bitiş zamanı >= sonraki segment başlangıç - threshold
            if current["end_time"] >= next_segment["start_time"] - self.merge_threshold:
                # Çakışma var, birleştir
                current["end_time"] = max(current["end_time"], next_segment["end_time"])
                current["frames"].append(next_segment["frame"])

                # En yüksek skoru koru
                if next_segment["score"] > current["score"]:
                    current["score"] = next_segment["score"]
                    current["frame"] = next_segment["frame"]

                logger.debug(
                    f"Merged segment at {next_segment['start_time']:.2f}s into "
                    f"[{current['start_time']:.2f}s - {current['end_time']:.2f}s]"
                )
            else:
                # Çakışma yok, mevcut segmenti kaydet ve yenisine geç
                merged.append(self._create_video_segment(current))

                current = next_segment.copy()
                current["frames"] = [current["frame"]]

        # Son segmenti ekle
        merged.append(self._create_video_segment(current))

        return merged

    def _create_video_segment(self, segment_data: Dict) -> VideoSegment:
        """
        İşlenmiş segment verisinden VideoSegment nesnesi oluşturur.

        Args:
            segment_data: İşlenmiş segment verisi

        Returns:
            VideoSegment nesnesi
        """
        best_frame = segment_data["frame"]

        return VideoSegment(
            video_id=segment_data["video_id"],
            start_time=round(segment_data["start_time"], 2),
            end_time=round(segment_data["end_time"], 2),
            best_score=round(segment_data["score"], 4),
            best_frame={
                "frame_id": best_frame["frame_metadata"].frame_id,
                "timestamp": best_frame["frame_metadata"].timestamp,
                "rank": best_frame["rank"],
                "thumbnail_url": f"/frames/{best_frame['frame_metadata'].video_id}/"
                f"{best_frame['frame_metadata'].frame_path.split('/')[-1]}",
            },
            frame_count=len(segment_data["frames"]),
        )

    def get_segment_summary(self, segments: List[VideoSegment]) -> Dict:
        """
        Birleştirilmiş segmentler hakkında özet bilgi döndürür.

        Args:
            segments: VideoSegment listesi

        Returns:
            Özet istatistikler
        """
        if not segments:
            return {"total_segments": 0, "total_duration": 0.0, "videos": []}

        video_stats = {}
        total_duration = 0.0

        for segment in segments:
            duration = segment.end_time - segment.start_time
            total_duration += duration

            if segment.video_id not in video_stats:
                video_stats[segment.video_id] = {
                    "segment_count": 0,
                    "total_duration": 0.0,
                    "best_score": 0.0,
                }

            video_stats[segment.video_id]["segment_count"] += 1
            video_stats[segment.video_id]["total_duration"] += duration
            video_stats[segment.video_id]["best_score"] = max(
                video_stats[segment.video_id]["best_score"], segment.best_score
            )

        return {
            "total_segments": len(segments),
            "total_duration": round(total_duration, 2),
            "unique_videos": len(video_stats),
            "videos": video_stats,
        }
