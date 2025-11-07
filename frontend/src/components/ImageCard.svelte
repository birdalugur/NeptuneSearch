<!--
Arama sonucu frame'leri gösterir ve tıklandığında video segment'ini oynatır.
-->

<script>
  import { getFrameUrl, getVideoSegment } from "../utils/api";
  import { videoStore } from "../stores/videoStore";
  import { createEventDispatcher } from "svelte";

  export let result;

  const dispatch = createEventDispatcher();

  $: imageUrl = getFrameUrl(result.thumbnail_url);

  /**
   * Frame'e tıklandığında video segment'ini oynatır
   */
  async function handleClick() {
    try {
      const segmentInfo = await getVideoSegment(
        result.video_id,
        result.timestamp,
      );
      videoStore.setSegment(segmentInfo);
      dispatch("play", segmentInfo);
    } catch (error) {
      console.error("Error getting video segment:", error);
      alert("Failed to load video segment");
    }
  }

  /**
   * Zaman formatı
   */
  function formatTimestamp(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }
</script>

<div
  class="card"
  on:click={handleClick}
  role="button"
  tabindex="0"
  on:keypress={(e) => e.key === "Enter" && handleClick()}
>
  <div class="image-container">
    <img
      src={imageUrl}
      alt="Result frame at {formatTimestamp(result.timestamp)}"
    />

    <div class="overlay">
      <div class="play-icon">▶</div>
    </div>
  </div>

  <div class="card-info">
    <div class="timestamp">
      ⏱️ {formatTimestamp(result.timestamp)}
    </div>

    <div class="score">
      <span class="score-label">Match:</span>
      <span class="score-value">{(result.score * 100).toFixed(1)}%</span>
    </div>
  </div>
</div>

<style>
  .card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
    cursor: pointer;
  }

  .card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  }

  .image-container {
    position: relative;
    width: 100%;
    height: 200px;
    overflow: hidden;
  }

  .image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .card:hover .overlay {
    opacity: 1;
  }

  .play-icon {
    font-size: 3rem;
    color: white;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  }

  .card-info {
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .timestamp {
    font-weight: 600;
    color: #111e68;
    font-size: 0.95rem;
  }

  .score {
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }

  .score-label {
    font-size: 0.85rem;
    color: #666;
  }

  .score-value {
    font-weight: 600;
    color: #28a745;
    font-size: 0.9rem;
  }

  @media (max-width: 768px) {
    .image-container {
      height: 150px;
    }

    .card-info {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
  }
</style>
