<script>
  import ImageCard from "./ImageCard.svelte";
  import SegmentCard from "./SegmentCard.svelte";
  import { maxResults } from "../stores/filterStore";

  export let results = [];
  export let segments = [];

  let showSegments = true;

  $: displayItems = showSegments && segments.length > 0 ? segments : results;
  $: visibleItems = displayItems.slice(0, $maxResults);
  $: hasMoreItems = displayItems.length > $maxResults;
</script>

{#if results.length > 0 || segments.length > 0}
  <div class="mb-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-primary text-xl">
        Showing {visibleItems.length} of {displayItems.length}
        {showSegments && segments.length > 0 ? "segments" : "frames"}
      </h3>

      {#if segments.length > 0}
        <div class="flex gap-2">
          <button
            class="px-4 py-2 rounded-lg font-medium transition-all duration-200
                   {showSegments
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
            on:click={() => (showSegments = true)}
          >
            📊 Segments ({segments.length})
          </button>
          <button
            class="px-4 py-2 rounded-lg font-medium transition-all duration-200
                   {!showSegments
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
            on:click={() => (showSegments = false)}
          >
            🖼️ Frames ({results.length})
          </button>
        </div>
      {/if}
    </div>

    <p class="text-gray-600 text-sm text-center">
      Click on any {showSegments && segments.length > 0 ? "segment" : "frame"} to
      play the video
    </p>
  </div>

  <div
    class="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] md:grid-cols-[repeat(auto-fill,minmax(240px,1fr))] sm:grid-cols-1 gap-6 md:gap-4 max-w-[1600px] mx-auto mb-8"
  >
    {#each visibleItems as item (showSegments && segments.length > 0 ? `${item.video_id}-${item.start_time}` : item.frame_id)}
      {#if showSegments && segments.length > 0}
        <SegmentCard segment={item} />
      {:else}
        <ImageCard result={item} />
      {/if}
    {/each}
  </div>

  {#if hasMoreItems}
    <div
      class="text-center p-4 bg-[#f5f7ff] rounded-xl text-gray-600 text-sm mt-4"
    >
      {displayItems.length - $maxResults} more {showSegments &&
      segments.length > 0
        ? "segments"
        : "results"} available. Adjust Top K filter to see more.
    </div>
  {/if}
{:else}
  <div class="text-center py-16 px-8 text-gray-600">
    <div class="text-6xl mb-4 opacity-50">🔍</div>
    <p class="text-lg">No results found. Try a different search query.</p>
  </div>
{/if}
