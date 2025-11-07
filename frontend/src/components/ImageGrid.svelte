<!--
Arama sonuçlarını grid layout ile gösterir.
-->

<script>
  import ImageCard from './ImageCard.svelte';
  import { maxResults } from '../stores/filterStore';
  
  export let results = [];
  
  $: visibleResults = results.slice(0, $maxResults);
  $: hasMoreResults = results.length > $maxResults;
</script>

{#if results.length > 0}
  <div class="results-header">
    <h3>
      Showing {visibleResults.length} of {results.length} results
    </h3>
    <p class="hint">Click on any frame to play the video segment</p>
  </div>
  
  <div class="grid">
    {#each visibleResults as result (result.frame_id)}
      <ImageCard {result} />
    {/each}
  </div>
  
  {#if hasMoreResults}
    <div class="more-results-hint">
      {results.length - $maxResults} more results available. Adjust Top K filter to see more.
    </div>
  {/if}
{:else}
  <div class="no-results">
    <div class="no-results-icon">🔍</div>
    <p>No results found. Try a different search query.</p>
  </div>
{/if}

<style>
  .results-header {
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .results-header h3 {
    margin: 0 0 0.5rem 0;
    color: #111e68;
    font-size: 1.3rem;
  }
  
  .hint {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
    max-width: 1600px;
    margin: 0 auto 2rem auto;
  }
  
  .more-results-hint {
    text-align: center;
    padding: 1rem;
    background: #f5f7ff;
    border-radius: 10px;
    color: #666;
    font-size: 0.9rem;
    margin-top: 1rem;
  }
  
  .no-results {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
  }
  
  .no-results-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  .no-results p {
    font-size: 1.1rem;
    margin: 0;
  }
  
  @media (max-width: 768px) {
    .grid {
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 1rem;
    }
  }
  
  @media (max-width: 480px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>