<script>
  import { onMount } from 'svelte';
  import { selectedVideo } from '../stores/videoStore';

  // Local state
  let videos = [];
  let loading = false;
  let error = null;

  // Fetch available videos from backend
  async function fetchVideos() {
    loading = true;
    error = null;
    try {
      const resp = await fetch('http://localhost:8000/api/videos');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      // backend returns {"videos": [...], "total": n}
      videos = data.videos || [];
    } catch (e) {
      error = e.message || 'Failed to load videos';
      videos = [];
      console.error('fetchVideos error', e);
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
  }
</script>

<div class="video-selector">
  <h3>Choose a video</h3>
  {#if loading}
    <div>Loading videos...</div>
  {:else}
    {#if error}
      <div class="error">Error: {error}</div>
    {/if}
    {#if videos.length === 0}
      <div>No videos indexed. Upload a video via backend first.</div>
    {:else}
      <div class="list">
        {#each videos as v}
          <button class="video-item" on:click={() => chooseVideo(v)}>
            <div class="title">{v.original_filename}</div>
            <div class="meta">{Math.round(v.duration)}s · {v.width}x{v.height}</div>
          </button>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .video-selector { margin-bottom: 1.25rem; text-align: center; }
  .list { display:flex; gap:0.5rem; flex-wrap:wrap; justify-content:center; }
  .video-item {
    border-radius: 10px;
    padding: 0.5rem 1rem;
    background: white;
    border: 1px solid #e6e9f2;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  }
  .video-item:hover { transform: translateY(-3px); }
  .title { font-weight:600; color:#0d1548; }
  .meta { font-size:0.85rem; color:#556; }
</style>
