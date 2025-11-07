<script>
  import { createEventDispatcher } from 'svelte';
  import { maxResults } from '../stores/filterStore';
  
  const dispatch = createEventDispatcher();
  
  let activeK = 10;
  
  function filterResults(k) {
    activeK = k;
    maxResults.set(k);
    dispatch('filter', k);
  }
</script>

<div class="top-k-buttons">
  <button 
    type="button" 
    class:active={activeK === 5}
    on:click={() => filterResults(5)}
  >
    Top 5
  </button>
  <button 
    type="button" 
    class:active={activeK === 10}
    on:click={() => filterResults(10)}
  >
    Top 10
  </button>
  <button 
    type="button" 
    class:active={activeK === 30}
    on:click={() => filterResults(30)}
  >
    Top 30
  </button>
</div>

<style>
  .top-k-buttons {
    display: flex;
    gap: 0.5rem;
  }

  button {
    background-color: #111e68;
    color: white;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
  }

  button:hover {
    background-color: #1f2e9f;
    transform: translateY(-2px);
  }

  button.active {
    background-color: #0d1548;
  }
</style>