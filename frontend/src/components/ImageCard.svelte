<script>
  import { getFrameUrl, getVideoSegment } from "../utils/api";
  import { videoStore } from "../stores/videoStore";
  import { createEventDispatcher } from "svelte";

  export let result;

  const dispatch = createEventDispatcher();

  $: imageUrl = getFrameUrl(result.thumbnail_url);
  $: matchPercentage = (result.score * 100).toFixed(1);
  $: matchColor =
    result.score > 0.7
      ? "text-green-600"
      : result.score > 0.4
        ? "text-yellow-600"
        : "text-orange-600";

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
      dispatch("error", "Failed to load video segment");
    }
  }

  function formatTimestamp(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }
</script>

<div
  class="group bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-200
         hover:shadow-xl hover:border-blue-300 transition-all duration-300 cursor-pointer
         hover:-translate-y-2 active:translate-y-0"
  on:click={handleClick}
  role="button"
  tabindex="0"
  on:keypress={(e) => e.key === "Enter" && handleClick()}
>
  <div class="relative w-full aspect-video overflow-hidden bg-gray-100">
    <img
      src={imageUrl}
      alt="Video frame at {formatTimestamp(result.timestamp)}"
      class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      loading="lazy"
    />

    <!-- Hover overlay -->
    <div
      class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent
                opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-end p-4"
    >
      <div class="text-white text-center w-full">
        <div class="text-2xl mb-1">▶</div>
        <div class="text-sm font-medium">Click to play</div>
      </div>
    </div>

    <!-- Timestamp badge -->
    <div
      class="absolute top-3 left-3 bg-black/80 text-white px-2 py-1 rounded-lg text-sm font-medium"
    >
      ⏱️ {formatTimestamp(result.timestamp)}
    </div>
  </div>

  <div class="p-4">
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-600">Confidence:</div>
      <div class="flex items-center gap-2">
        <div class={`font-bold ${matchColor}`}>
          {matchPercentage}%
        </div>
        <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full transition-all duration-500 rounded-full"
            class:bg-green-500={result.score > 0.7}
            class:bg-yellow-500={result.score <= 0.7 && result.score > 0.4}
            class:bg-orange-500={result.score <= 0.4}
            style={`width: ${matchPercentage}%`}
          ></div>
        </div>
      </div>
    </div>
  </div>
</div>
