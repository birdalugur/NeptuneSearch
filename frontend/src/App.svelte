<!-- frontend/src/App.svelte -->
<script>
  import VideoUploader from "./components/VideoUploader.svelte";
  import SearchForm from "./components/SearchForm.svelte";
  import ImageGrid from "./components/ImageGrid.svelte";
  import VideoPlayer from "./components/VideoPlayer.svelte";
  import VideoSelector from "./components/VideoSelector.svelte";
  import Notification from "./components/Notification.svelte";
  import { search } from "./utils/api";
  import { selectedVideo } from "./stores/videoStore";

  let results = [];
  let query = "";
  let loading = false;
  let notifications = [];

  function handleVideoUploaded(event) {
    showNotification(
      "Video processed successfully! You can now search.",
      "success",
    );
  }

  function showNotification(message, type = "info") {
    const id = Date.now();
    notifications = [...notifications, { id, message, type }];

    setTimeout(() => {
      notifications = notifications.filter((n) => n.id !== id);
    }, 5000);
  }

  function removeNotification(id) {
    notifications = notifications.filter((n) => n.id !== id);
  }

  async function handleSearch(searchQuery) {
    if (!$selectedVideo || !$selectedVideo.video_id) {
      showNotification("Please select a video first!", "error");
      return;
    }

    query = searchQuery;
    loading = true;

    try {
      const response = await search($selectedVideo.video_id, searchQuery);
      results = response.results || [];

      if (results.length === 0) {
        showNotification(
          "No matching frames found. Try a different query.",
          "warning",
        );
      } else {
        showNotification(`Found ${results.length} matching frames!`, "success");
      }
    } catch (err) {
      console.error("Search failed:", err);
      showNotification(
        err.message || "Search failed. Please try again.",
        "error",
      );
      results = [];
    } finally {
      loading = false;
    }
  }
</script>

<main
  class="bg-gradient-to-br from-white to-gray-50 min-h-screen p-4 md:p-6 font-sans text-gray-900"
>
  <div class="max-w-7xl mx-auto">
    <!-- Notifications Container -->
    <div class="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {#each notifications as notification}
        <Notification
          {notification}
          on:close={() => removeNotification(notification.id)}
        />
      {/each}
    </div>

    <!-- Header -->
    <div class="text-center mb-8">
      <div class="mb-6">
        <img src="logo.png" alt="Neptune Search" class="h-24 mx-auto" />
      </div>
      <h1
        class="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4"
      >
        Video Semantic Search
      </h1>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto">
        Upload a video and search for specific moments using natural language AI
      </p>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column - Upload & Selection -->
      <div class="lg:col-span-1 space-y-6">
        <VideoUploader on:uploaded={handleVideoUploaded} />
        <VideoSelector />
      </div>

      <!-- Right Column - Search & Results -->
      <div class="lg:col-span-2">
        <SearchForm
          on:search={(e) => handleSearch(e.detail)}
          {query}
          hasResults={results.length > 0}
        />

        {#if loading}
          <div class="text-center py-12">
            <div class="inline-flex flex-col items-center">
              <div
                class="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"
              ></div>
              <p class="text-lg text-gray-600 font-medium">
                Searching through video frames...
              </p>
              <p class="text-sm text-gray-500 mt-2">
                Analyzing content with AI
              </p>
            </div>
          </div>
        {/if}

        {#if !loading && results.length > 0}
          <div
            class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <ImageGrid {results} />
          </div>
        {/if}
      </div>
    </div>

    <VideoPlayer />
  </div>
</main>
