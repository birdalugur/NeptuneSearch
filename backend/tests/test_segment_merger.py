"""
Segment Merger Kullanım Örneği ve Test

Bu dosya segment_merger modülünün nasıl kullanılacağını gösterir.
"""

from core.segment_merger import SegmentMerger
from core.video_processor import FrameMetadata


def test_segment_merger():
    """Segment merger işlevselliğini test eder."""

    # Örnek arama sonuçları (simüle edilmiş)
    mock_search_results = [
        {
            "rank": 1,
            "score": 0.95,
            "frame_metadata": FrameMetadata(
                frame_id="video1_frame_000001",
                video_id="video1",
                frame_path="/frames/video1/video1_frame_000001.jpg",
                timestamp=10.5,
                frame_number=105,
            ),
        },
        {
            "rank": 2,
            "score": 0.92,
            "frame_metadata": FrameMetadata(
                frame_id="video1_frame_000002",
                video_id="video1",
                frame_path="/frames/video1/video1_frame_000002.jpg",
                timestamp=12.0,
                frame_number=120,
            ),
        },
        {
            "rank": 3,
            "score": 0.88,
            "frame_metadata": FrameMetadata(
                frame_id="video1_frame_000003",
                video_id="video1",
                frame_path="/frames/video1/video1_frame_000003.jpg",
                timestamp=14.5,
                frame_number=145,
            ),
        },
        {
            "rank": 4,
            "score": 0.85,
            "frame_metadata": FrameMetadata(
                frame_id="video1_frame_000004",
                video_id="video1",
                frame_path="/frames/video1/video1_frame_000004.jpg",
                timestamp=30.0,
                frame_number=300,
            ),
        },
        {
            "rank": 5,
            "score": 0.80,
            "frame_metadata": FrameMetadata(
                frame_id="video2_frame_000001",
                video_id="video2",
                frame_path="/frames/video2/video2_frame_000001.jpg",
                timestamp=5.0,
                frame_number=50,
            ),
        },
    ]

    # Segment merger oluştur
    merger = SegmentMerger(merge_threshold=0.0)

    # Segmentleri birleştir
    merged_segments = merger.merge_search_results(
        mock_search_results, segment_duration=10.0
    )

    # Sonuçları yazdır
    print("=" * 80)
    print("SEGMENT BİRLEŞTİRME SONUÇLARI")
    print("=" * 80)
    print(f"\nToplam frame sayısı: {len(mock_search_results)}")
    print(f"Birleştirilmiş segment sayısı: {len(merged_segments)}")
    print()

    for i, segment in enumerate(merged_segments, 1):
        print(f"Segment {i}:")
        print(f"  Video ID: {segment.video_id}")
        print(f"  Zaman Aralığı: {segment.start_time:.2f}s - {segment.end_time:.2f}s")
        print(f"  Süre: {segment.end_time - segment.start_time:.2f}s")
        print(f"  En İyi Skor: {segment.best_score:.4f}")
        print(f"  Frame Sayısı: {segment.frame_count}")
        print(f"  En İyi Frame: {segment.best_frame['frame_id']}")
        print()

    # Özet istatistikler
    summary = merger.get_segment_summary(merged_segments)
    print("=" * 80)
    print("ÖZET İSTATİSTİKLER")
    print("=" * 80)
    print(f"Toplam Segment: {summary['total_segments']}")
    print(f"Toplam Süre: {summary['total_duration']:.2f} saniye")
    print(f"Benzersiz Video Sayısı: {summary['unique_videos']}")
    print()

    for video_id, stats in summary["videos"].items():
        print(f"Video: {video_id}")
        print(f"  Segment Sayısı: {stats['segment_count']}")
        print(f"  Toplam Süre: {stats['total_duration']:.2f}s")
        print(f"  En İyi Skor: {stats['best_score']:.4f}")
        print()


def example_api_response():
    """API'den dönecek örnek response yapısını gösterir."""

    print("=" * 80)
    print("ÖRN EK API RESPONSE YAPISI")
    print("=" * 80)
    print("""
{
  "query": "cat playing with toy",
  "video_id": null,
  "results": [
    {
      "frame_id": "video1_frame_000001",
      "video_id": "video1",
      "timestamp": 10.5,
      "score": 0.95,
      "rank": 1,
      "thumbnail_url": "/frames/video1/video1_frame_000001.jpg"
    },
    ...
  ],
  "total_results": 5,
  "segments": [
    {
      "video_id": "video1",
      "start_time": 5.5,
      "end_time": 19.5,
      "duration": 14.0,
      "best_score": 0.95,
      "best_frame": {
        "frame_id": "video1_frame_000001",
        "timestamp": 10.5,
        "rank": 1,
        "thumbnail_url": "/frames/video1/video1_frame_000001.jpg"
      },
      "frame_count": 3
    },
    {
      "video_id": "video1",
      "start_time": 25.0,
      "end_time": 35.0,
      "duration": 10.0,
      "best_score": 0.85,
      "best_frame": {
        "frame_id": "video1_frame_000004",
        "timestamp": 30.0,
        "rank": 4,
        "thumbnail_url": "/frames/video1/video1_frame_000004.jpg"
      },
      "frame_count": 1
    }
  ],
  "merge_info": {
    "total_segments": 2,
    "total_duration": 24.0,
    "unique_videos": 1,
    "videos": {
      "video1": {
        "segment_count": 2,
        "total_duration": 24.0,
        "best_score": 0.95
      }
    }
  }
}
    """)


def explain_algorithm():
    """Algoritmanın nasıl çalıştığını açıklar."""

    print("=" * 80)
    print("ALGORİTMA AÇIKLAMASI")
    print("=" * 80)
    print("""
1. GRUPLAMA (Grouping):
   - Arama sonuçları video_id'ye göre gruplandırılır
   - Farklı videoların segmentleri asla birleştirilmez
   
2. SIRALAMA (Sorting):
   - Her video için frame'ler timestamp'e göre sıralanır
   - Bu, birleştirme algoritmasının çalışması için gereklidir
   
3. SEGMENT OLUŞTURMA:
   - Her frame için bir segment oluşturulur
   - Segment: [timestamp - 5s, timestamp + 5s] (toplam 10 saniye)
   
4. BİRLEŞTİRME (Merge Intervals):
   - Sıralanmış segmentler üzerinde döngü kurulur
   - Eğer Mevcut.Start_Time <= Önceki.End_Time ise:
     * Segmentler çakışıyor, birleştirilir
     * Yeni End_Time = max(Önceki.End, Mevcut.End)
     * En yüksek skora sahip frame korunur
   - Eğer çakışma yoksa:
     * Önceki segment sonuç listesine eklenir
     * Yeni segmente geçilir

5. SONUÇ:
   - Her video için birleştirilmiş segmentler döndürülür
   - Tüm segmentler skor sırasına göre dizilir
   - Her segment en iyi frame bilgisini içerir

ÖRNEK:
  Frame 1: timestamp=10s, score=0.95  → Segment: [5s - 15s]
  Frame 2: timestamp=12s, score=0.92  → Segment: [7s - 17s]
  Frame 3: timestamp=30s, score=0.88  → Segment: [25s - 35s]
  
  Birleştirme Sonrası:
  - Segment 1: [5s - 17s], best_score=0.95, frame_count=2
  - Segment 2: [25s - 35s], best_score=0.88, frame_count=1
    """)


if __name__ == "__main__":
    print("\n" * 2)
    explain_algorithm()
    print("\n" * 2)
    test_segment_merger()
    print("\n" * 2)
    example_api_response()
