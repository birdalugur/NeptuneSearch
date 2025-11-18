<script>
  import { onMount } from "svelte";
  import { selectedVideo, uploadedVideo } from "../stores/videoStore";

  let videos = [];
  let loading = false;
  let error = null;
  let retryCount = 0;

  async function fetchVideos() {
    loading = true;
    error = null;
    try {
      const resp = await fetch("http://localhost:8000/api/videos");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      videos = data.videos || [];
      retryCount = 0;
    } catch (e) {
      error = e.message || "Failed to load videos";
      videos = [];
      console.error("fetchVideos error", e);
    } finally {
      loading = false;
    }
  }

  async function retryWithBackoff() {
    retryCount++;
    const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);
    await new Promise((resolve) => setTimeout(resolve, delay));
    await fetchVideos();
  }

  function chooseVideo(v) {
    selectedVideo.set(v);
    uploadedVideo.set(v);
  }

  function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }

  onMount(() => {
    fetchVideos();
  });
</script>

<div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
  <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
    <span class="text-blue-600">🎬</span>
    Select Video
  </h3>

  {#if loading}
    <div class="text-center py-8">
      <div
        class="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-3"
      ></div>
      <p class="text-gray-600">Loading available videos...</p>
    </div>
  {:else if error}
    <div class="text-center py-6 bg-red-50 rounded-xl">
      <div class="text-red-600 mb-3">❌ Failed to load videos</div>
      <button
        on:click={retryWithBackoff}
        class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
      >
        Retry
      </button>
    </div>
  {:else if videos.length === 0}
    <div class="text-center py-8 bg-gray-50 rounded-xl">
      <div class="text-4xl mb-3 opacity-50">📹</div>
      <p class="text-gray-600 mb-2">No videos available</p>
      <p class="text-sm text-gray-500">Upload a video to get started</p>
    </div>
  {:else}
    <div class="space-y-3 max-h-80 overflow-y-auto">
      {#each videos as v}
        <button
          class="w-full text-left p-4 rounded-xl border-2 transition-all duration-200
                 hover:border-blue-300 hover:bg-blue-50 hover:shadow-sm
                 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                 {selectedVideo?.video_id === v.video_id
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 bg-white'}"
          on:click={() => chooseVideo(v)}
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-gray-900 truncate mb-1">
                {v.original_filename}
              </div>
              <div class="flex items-center gap-4 text-sm text-gray-600">
                <span class="flex items-center gap-1">
                  ⏱️ {formatDuration(v.duration)}
                </span>
                <span class="flex items-center gap-1">
                  📐 {v.width}x{v.height}
                </span>
                {#if v.total_frames}
                  <span class="flex items-center gap-1">
                    🖼️ {v.total_frames} frames
                  </span>
                {/if}
              </div>
            </div>
            {#if selectedVideo?.video_id === v.video_id}
              <div class="flex-shrink-0 text-blue-600 ml-3">✓</div>
            {/if}
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
