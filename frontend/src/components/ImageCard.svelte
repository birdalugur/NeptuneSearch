<script>
  import { getFrameUrl, getVideoSegment } from "../utils/api";
  import { videoStore } from "../stores/videoStore";
  import { createEventDispatcher } from "svelte";

  export let result;

  const dispatch = createEventDispatcher();

  $: imageUrl = getFrameUrl(result.thumbnail_url);

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

  function formatTimestamp(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }
</script>

<div
  class="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer hover:-translate-y-1.5 group"
  on:click={handleClick}
  role="button"
  tabindex="0"
  on:keypress={(e) => e.key === "Enter" && handleClick()}
>
  <div class="relative w-full h-[200px] md:h-[150px] overflow-hidden">
    <img
      src={imageUrl}
      alt="Result frame at {formatTimestamp(result.timestamp)}"
      class="w-full h-full object-cover block"
    />

    <div
      class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
    >
      <div class="text-5xl text-white drop-shadow-lg">▶</div>
    </div>
  </div>

  <div
    class="p-4 flex justify-between items-center md:flex-col md:items-start md:gap-2"
  >
    <div class="font-semibold text-primary text-[0.95rem]">
      ⏱️ {formatTimestamp(result.timestamp)}
    </div>

    <div class="flex items-center gap-1">
      <span class="text-[0.85rem] text-gray-600">Match:</span>
      <span class="font-semibold text-green-600 text-[0.9rem]">
        {(result.score * 100).toFixed(1)}%
      </span>
    </div>
  </div>
</div>
