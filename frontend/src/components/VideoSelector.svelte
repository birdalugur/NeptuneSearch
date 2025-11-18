<script>
  import { onMount } from "svelte";
  import { selectedVideo, uploadedVideo } from "../stores/videoStore";

  // Local state
  let videos = [];
  let loading = false;
  let error = null;

  // Fetch available videos from backend
  async function fetchVideos() {
    loading = true;
    error = null;
    try {
      const resp = await fetch("http://localhost:8000/api/videos");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      // backend returns {"videos": [...], "total": n}
      videos = data.videos || [];
    } catch (e) {
      error = e.message || "Failed to load videos";
      videos = [];
      console.error("fetchVideos error", e);
    } finally {
      loading = false;
    }
  }

  // On mount, load videos
  onMount(() => {
    fetchVideos();
  });

  // Select video helper
  function chooseVideo(v) {
    selectedVideo.set(v);
    uploadedVideo.set(v);
  }
</script>

<div class="mb-5 text-center">
  <h3>Choose a video</h3>
  {#if loading}
    <div>Loading videos...</div>
  {:else}
    {#if error}
      <div class="text-red-600">Error: {error}</div>
    {/if}
    {#if videos.length === 0}
      <div>No videos indexed. Upload a video via backend first.</div>
    {:else}
      <div class="flex gap-2 flex-wrap justify-center">
        {#each videos as v}
          <button
            class="rounded-lg py-2 px-4 bg-white border border-gray-200 cursor-pointer shadow-sm transform transition-transform hover:-translate-y-1 focus:outline-none"
            on:click={() => chooseVideo(v)}
          >
            <div class="font-semibold text-[#0d1548]">
              {v.original_filename}
            </div>
            <div class="text-sm text-gray-600">
              {Math.round(v.duration)}s · {v.width}x{v.height}
            </div>
          </button>
        {/each}
      </div>
    {/if}
  {/if}
</div>
