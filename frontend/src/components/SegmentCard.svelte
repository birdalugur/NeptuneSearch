<script>
  import { getFrameUrl } from "../utils/api";
  import { videoStore } from "../stores/videoStore";
  import { createEventDispatcher } from "svelte";

  export let segment;

  const dispatch = createEventDispatcher();

  $: imageUrl = getFrameUrl(segment.best_frame.thumbnail_url);
  $: matchPercentage = (segment.best_score * 100).toFixed(1);
  $: matchColor =
    segment.best_score > 0.7
      ? "text-green-600"
      : segment.best_score > 0.4
        ? "text-yellow-600"
        : "text-orange-600";
  $: segmentDuration = segment.duration || (segment.end_time - segment.start_time);

  async function handleClick() {
    try {
      // Segment bilgisi zaten mevcut, direkt video player'a gönder
      videoStore.setSegment(segment);
      dispatch("play", segment);
    } catch (error) {
      console.error("Error loading segment:", error);
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
         hover:shadow-xl hover:border-purple-300 transition-all duration-300 cursor-pointer
         hover:-translate-y-2 active:translate-y-0"
  on:click={handleClick}
  role="button"
  tabindex="0"
  on:keypress={(e) => e.key === "Enter" && handleClick()}
>
  <div class="relative w-full aspect-video overflow-hidden bg-gray-100">
    <img
      src={imageUrl}
      alt="Video segment {formatTimestamp(segment.start_time)} - {formatTimestamp(segment.end_time)}"
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
        <div class="text-sm font-medium">Click to play segment</div>
      </div>
    </div>

    <!-- Segment Duration badge -->
    <div
      class="absolute top-3 left-3 bg-purple-600/90 text-white px-3 py-1 rounded-lg text-sm font-semibold"
    >
      📹 {segmentDuration.toFixed(1)}s
    </div>

    <!-- Frame Count badge -->
    {#if segment.frame_count > 1}
      <div
        class="absolute top-3 right-3 bg-blue-600/90 text-white px-2 py-1 rounded-lg text-xs font-medium"
      >
        {segment.frame_count} frames
      </div>
    {/if}
  </div>

  <div class="p-4">
    <!-- Time Range -->
    <div class="mb-3 flex items-center justify-between text-sm">
      <div class="text-gray-600 font-medium">
        ⏱️ {formatTimestamp(segment.start_time)} - {formatTimestamp(segment.end_time)}
      </div>
    </div>

    <!-- Confidence Score -->
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-600">Best Match:</div>
      <div class="flex items-center gap-2">
        <div class={`font-bold ${matchColor}`}>
          {matchPercentage}%
        </div>
        <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full transition-all duration-500 rounded-full"
            class:bg-green-500={segment.best_score > 0.7}
            class:bg-yellow-500={segment.best_score <= 0.7 && segment.best_score > 0.4}
            class:bg-orange-500={segment.best_score <= 0.4}
            style={`width: ${matchPercentage}%`}
          ></div>
        </div>
      </div>
    </div>
  </div>
</div>