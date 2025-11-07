<script>
  import { videoSegment } from "../stores/videoStore";
  import { getVideoUrl } from "../utils/api";
  import { onDestroy } from "svelte";

  let videoElement;
  let isPlaying = false;
  let currentTime = 0;
  let duration = 0;
  let currentSegmentId = null; // aynı segment tekrar yüklenmesin

  $: if ($videoSegment && videoElement) {
    // aynı segmentse tekrar yükleme
    if (
      currentSegmentId !==
      $videoSegment.video_id + ":" + $videoSegment.start_time
    ) {
      currentSegmentId =
        $videoSegment.video_id + ":" + $videoSegment.start_time;
      loadVideoSegment();
    }
  }

  async function loadVideoSegment() {
    if (!$videoSegment || !videoElement) return;

    try {
      const videoUrl = getVideoUrl($videoSegment.video_url);

      // Eski yüklemeyi sıfırla
      videoElement.pause();
      videoElement.removeAttribute("src");
      videoElement.load();

      // Yeni kaynak ayarla
      videoElement.src = videoUrl;

      // Bu flag ile üst üste play çağrısını engelle
      let hasPlayed = false;

      videoElement.onloadedmetadata = async () => {
        try {
          videoElement.currentTime = $videoSegment.start_time;
          duration = $videoSegment.duration;

          // metadata yüklenmişse tek seferlik play dene
          if (!hasPlayed) {
            hasPlayed = true;
            await playVideo();
          }
        } catch (err) {
          console.warn("Video play error:", err);
        }
      };

      videoElement.ontimeupdate = () => {
        if (!$videoSegment) return;
        currentTime = videoElement.currentTime - $videoSegment.start_time;

        if (videoElement.currentTime >= $videoSegment.end_time) {
          pauseVideo();
          videoElement.currentTime = $videoSegment.start_time;
        }
      };
    } catch (error) {
      console.error("Error loading video segment:", error);
    }
  }

  async function playVideo() {
    try {
      // Sessiz başlat, sonra kullanıcı isterse sesi açar
      videoElement.muted = true;
      await videoElement.play();
      isPlaying = true;
    } catch (error) {
      // AbortError gibi hataları sessize al
      if (error.name !== "AbortError") {
        console.error("Error playing video:", error);
      }
    }
  }

  function pauseVideo() {
    if (videoElement) {
      videoElement.pause();
      isPlaying = false;
    }
  }

  function togglePlayPause() {
    if (isPlaying) pauseVideo();
    else playVideo();
  }

  function restartVideo() {
    if (videoElement && $videoSegment) {
      videoElement.currentTime = $videoSegment.start_time;
      playVideo();
    }
  }

  function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }

  function closePlayer() {
    if (videoElement) pauseVideo();
    videoSegment.set(null);
    currentSegmentId = null;
  }

  onDestroy(() => {
    if (videoElement) {
      videoElement.pause();
      videoElement.removeAttribute("src");
      videoElement.load();
    }
  });
</script>

{#if $videoSegment}
  <div class="player-overlay" on:click={closePlayer}>
    <div class="player-container" on:click|stopPropagation>
      <div class="player-header">
        <h3>Video Playback</h3>
        <button class="close-btn" on:click={closePlayer}>✕</button>
      </div>

      <div class="video-wrapper">
        <video bind:this={videoElement} class="video-element" controls>
          Your browser does not support video playback.
        </video>
      </div>

      <div class="player-info">
        <div class="time-info">
          <span class="time-label">Playing:</span>
          <span class="time-value">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        <div class="segment-info">
          <span class="segment-label">Segment:</span>
          <span class="segment-value">
            {$videoSegment.start_time.toFixed(1)}s - {$videoSegment.end_time.toFixed(
              1,
            )}s
          </span>
        </div>
      </div>

      <div class="player-controls">
        <button class="control-btn" on:click={togglePlayPause}>
          {isPlaying ? "⏸️ Pause" : "▶️ Play"}
        </button>

        <button class="control-btn" on:click={restartVideo}>
          🔄 Restart
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .player-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .player-container {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 900px;
    max-height: 90vh;
    overflow: auto;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  }

  .player-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #eee;
  }

  .player-header h3 {
    margin: 0;
    color: #111e68;
    font-size: 1.3rem;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s ease;
  }

  .close-btn:hover {
    background-color: #f0f0f0;
    color: #111e68;
  }

  .video-wrapper {
    padding: 1.5rem;
    background: #000;
  }

  .video-element {
    width: 100%;
    max-height: 500px;
    border-radius: 8px;
  }

  .player-info {
    padding: 1rem 1.5rem;
    background: #f5f7ff;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .time-info,
  .segment-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .time-label,
  .segment-label {
    font-weight: 600;
    color: #666;
  }

  .time-value,
  .segment-value {
    color: #111e68;
    font-weight: 600;
  }

  .player-controls {
    padding: 1.5rem;
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .control-btn {
    background-color: #111e68;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition:
      background-color 0.3s ease,
      transform 0.2s ease;
  }

  .control-btn:hover {
    background-color: #1f2e9f;
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    .player-container {
      max-width: 95%;
    }

    .player-info {
      flex-direction: column;
      gap: 0.5rem;
    }

    .player-controls {
      flex-direction: column;
    }

    .control-btn {
      width: 100%;
    }
  }
</style>
