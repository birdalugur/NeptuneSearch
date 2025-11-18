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

      videoElement.pause();
      videoElement.removeAttribute("src");
      videoElement.load();
      videoElement.src = videoUrl;

      let hasPlayed = false;

      videoElement.onloadedmetadata = async () => {
        try {
          videoElement.currentTime = $videoSegment.start_time;
          duration = $videoSegment.duration;

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
      videoElement.muted = true;
      await videoElement.play();
      isPlaying = true;
    } catch (error) {
      if (error.name !== "AbortError")
        console.error("Error playing video:", error);
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
  <div
    class="fixed inset-0 bg-black/85 flex items-center justify-center z-[1000] p-4"
    on:click={closePlayer}
  >
    <div
      class="bg-white rounded-2xl w-full max-w-[900px] max-h-[90vh] overflow-auto shadow-2xl"
      on:click|stopPropagation
    >
      <div
        class="flex justify-between items-center p-6 border-b border-gray-200"
      >
        <h3 class="text-[#111e68] text-xl font-semibold">Video Playback</h3>
        <button
          class="text-gray-600 hover:bg-gray-100 hover:text-[#111e68] transition p-1 rounded-full w-8 h-8 flex items-center justify-center text-xl"
          on:click={closePlayer}
        >
          ✕
        </button>
      </div>

      <div class="p-6 bg-black">
        <video
          bind:this={videoElement}
          class="w-full max-h-[500px] rounded-lg"
          controls
        >
          Your browser does not support video playback.
        </video>
      </div>

      <div class="p-4 px-6 bg-[#f5f7ff] flex flex-wrap justify-between gap-4">
        <div class="flex items-center gap-2">
          <span class="font-semibold text-gray-600">Playing:</span>
          <span class="font-semibold text-[#111e68]">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        <div class="flex items-center gap-2">
          <span class="font-semibold text-gray-600">Segment:</span>
          <span class="font-semibold text-[#111e68]">
            {$videoSegment.start_time.toFixed(1)}s -
            {$videoSegment.end_time.toFixed(1)}s
          </span>
        </div>
      </div>

      <div class="p-6 flex gap-4 justify-center">
        <button
          class="bg-[#111e68] text-white font-semibold py-3 px-6 rounded-lg transition hover:bg-[#1f2e9f] hover:-translate-y-0.5"
          on:click={togglePlayPause}
        >
          {isPlaying ? "⏸️ Pause" : "▶️ Play"}
        </button>

        <button
          class="bg-[#111e68] text-white font-semibold py-3 px-6 rounded-lg transition hover:bg-[#1f2e9f] hover:-translate-y-0.5"
          on:click={restartVideo}
        >
          🔄 Restart
        </button>
      </div>
    </div>
  </div>
{/if}
