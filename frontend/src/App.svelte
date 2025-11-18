<script>
  import VideoUploader from "./components/VideoUploader.svelte";
  import SearchForm from "./components/SearchForm.svelte";
  import ImageGrid from "./components/ImageGrid.svelte";
  import VideoPlayer from "./components/VideoPlayer.svelte";
  import VideoSelector from "./components/VideoSelector.svelte";
  import { search } from "./utils/api";
  import { selectedVideo } from "./stores/videoStore";

  let results = [];
  let query = "";
  let loading = false;
  let error = null;

  function handleVideoUploaded(event) {
    console.log("Video uploaded:", event.detail);
    showNotification("Video processed successfully! You can now search.");
  }

  async function handleSearch(searchQuery) {
    if (!$selectedVideo || !$selectedVideo.video_id) {
      error = "Please select a video first!";
      showNotification(error, "error");
      return;
    }

    query = searchQuery;
    loading = true;
    error = null;

    try {
      const response = await search($selectedVideo.video_id, searchQuery);
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

<main class="bg-gradient-to-br from-white to-gray-100 min-h-screen p-8 md:p-4 font-sans text-primary">
  <div class="max-w-[1600px] mx-auto">
    <div class="text-center mb-8">
      <div class="mb-4">
        <img src="logo.png" alt="Logo" class="h-[140px] mx-auto" />
      </div>

      <h1 class="text-4xl md:text-3xl font-semibold mb-2">
        Video Semantic Search with AI
      </h1>
      <p class="text-lg text-gray-600">
        Upload a video and search for specific moments using natural language
      </p>
    </div>

    <VideoUploader on:uploaded={handleVideoUploaded} />
    <VideoSelector />

    <SearchForm
      on:search={(e) => handleSearch(e.detail)}
      {query}
      hasResults={results.length > 0}
    />

    {#if loading}
      <div class="text-center py-16 px-8">
        <div class="w-[50px] h-[50px] mx-auto mb-4 border-4 border-gray-300 border-t-primary rounded-full animate-spin-custom"></div>
        <p class="text-xl text-gray-600">Searching through video frames...</p>
      </div>
    {/if}

    {#if error}
      <div class="bg-red-50 text-red-700 p-4 rounded-xl text-center mb-8 font-semibold border-2 border-red-200">
        ⚠️ {error}
      </div>
    {/if}

    {#if !loading}
      <ImageGrid {results} />
    {/if}

    <VideoPlayer />
  </div>
</main>