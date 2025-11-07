<script>
  import VideoUploader from "./components/VideoUploader.svelte";
  import SearchForm from "./components/SearchForm.svelte";
  import ImageGrid from "./components/ImageGrid.svelte";
  import VideoPlayer from "./components/VideoPlayer.svelte";
  import { search } from "./utils/api";

  let results = [];
  let query = "";
  let loading = false;
  let error = null;

  /**
   * Video yüklendiğinde çağrılır
   */
  function handleVideoUploaded(event) {
    console.log("Video uploaded:", event.detail);
    showNotification("Video processed successfully! You can now search.");
  }

  /**
   * Arama işlemini gerçekleştirir
   */
  async function handleSearch(searchQuery) {
    query = searchQuery;
    loading = true;
    error = null;

    try {
      const response = await search(searchQuery);
      results = response.results || [];

      if (results.length === 0) {
        showNotification(
          "No matching frames found. Try a different query.",
          "warning",
        );
      }
    } catch (err) {
      console.error("Search failed:", err);
      error = err.message || "Search failed. Please try again.";
      results = [];
      showNotification(error, "error");
    } finally {
      loading = false;
    }
  }

  function showNotification(message, type = "info") {
    console.log(`[${type.toUpperCase()}] ${message}`);
  }
</script>

<main>
  <div class="header-container">
    <div class="logo-container">
      <img src="logo.png" alt="Logo" />
    </div>

    <h1>Video Semantic Search with AI</h1>
    <p class="subtitle">
      Upload a video and search for specific moments using natural language
    </p>
  </div>

  <VideoUploader on:uploaded={handleVideoUploaded} />

  <SearchForm
    on:search={(e) => handleSearch(e.detail)}
    {query}
    hasResults={results.length > 0}
  />

  <!-- Loading State -->
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Searching through video frames...</p>
    </div>
  {/if}

  {#if error}
    <div class="error-banner">
      ⚠️ {error}
    </div>
  {/if}

  <!-- Results Grid -->
  {#if !loading}
    <ImageGrid {results} />
  {/if}

  <VideoPlayer />
</main>

<style>
  :global(body) {
    background: linear-gradient(135deg, #ffffff, #f7f7f7);
    font-family: "Inter", sans-serif;
    color: #111e68;
    padding: 2rem;
    margin: 0;
    min-height: 100vh;
  }

  main {
    max-width: 1600px;
    margin: 0 auto;
  }

  .header-container {
    text-align: center;
    margin-bottom: 2rem;
  }

  .logo-container {
    margin-bottom: 1rem;
  }

  .logo-container img {
    height: 140px;
  }

  h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    font-weight: 600;
  }

  .subtitle {
    margin: 0;
    font-size: 1.1rem;
    color: #666;
  }

  .loading {
    text-align: center;
    padding: 4rem 2rem;
  }

  .spinner {
    width: 50px;
    height: 50px;
    margin: 0 auto 1rem;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #111e68;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .loading p {
    font-size: 1.2rem;
    color: #666;
    margin: 0;
  }

  .error-banner {
    background-color: #fee;
    color: #c00;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 600;
    border: 2px solid #fcc;
  }

  @media (max-width: 768px) {
    :global(body) {
      padding: 1rem;
    }

    h1 {
      font-size: 1.8rem;
    }

    .subtitle {
      font-size: 1rem;
    }
  }
</style>
