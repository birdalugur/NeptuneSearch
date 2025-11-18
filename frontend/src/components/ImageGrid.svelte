<script>
  import ImageCard from "./ImageCard.svelte";
  import { maxResults } from "../stores/filterStore";

  export let results = [];

  $: visibleResults = results.slice(0, $maxResults);
  $: hasMoreResults = results.length > $maxResults;
</script>

{#if results.length > 0}
  <div class="mb-6 text-center">
    <h3 class="text-primary text-xl mb-2">
      Showing {visibleResults.length} of {results.length} results
    </h3>
    <p class="text-gray-600 text-sm">
      Click on any frame to play the video segment
    </p>
  </div>

  <div
    class="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] md:grid-cols-[repeat(auto-fill,minmax(240px,1fr))] sm:grid-cols-1 gap-6 md:gap-4 max-w-[1600px] mx-auto mb-8"
  >
    {#each visibleResults as result (result.frame_id)}
      <ImageCard {result} />
    {/each}
  </div>

  {#if hasMoreResults}
    <div
      class="text-center p-4 bg-[#f5f7ff] rounded-xl text-gray-600 text-sm mt-4"
    >
      {results.length - $maxResults} more results available. Adjust Top K filter
      to see more.
    </div>
  {/if}
{:else}
  <div class="text-center py-16 px-8 text-gray-600">
    <div class="text-6xl mb-4 opacity-50">🔍</div>
    <p class="text-lg">No results found. Try a different search query.</p>
  </div>
{/if}
