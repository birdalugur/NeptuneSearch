<script>
  import { uploadVideo } from "../utils/api";
  import {
    videoStore,
    isUploading,
    uploadProgress,
    uploadedVideo,
  } from "../stores/videoStore";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let fileInput;
  let selectedFile = null;
  let error = null;

  const acceptedFormats = ".mp4,.avi,.mov,.mkv,.webm";
  const maxSizeMB = 500;

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      error = `Video file is too large. Maximum size is ${maxSizeMB}MB`;
      selectedFile = null;
      return;
    }

    selectedFile = file;
    error = null;
  }

  async function handleUpload() {
    if (!selectedFile) return;

    try {
      error = null;
      videoStore.setUploading(true);
      videoStore.updateProgress(0);

      const response = await uploadVideo(selectedFile, (progress) => {
        videoStore.updateProgress(progress);
      });

      if (response.success) {
        videoStore.setVideo(response.video_info);
        dispatch("uploaded", response.video_info);
        selectedFile = null;
        fileInput.value = "";
      } else {
        error = response.message || "Upload failed";
      }
    } catch (err) {
      error = err.message || "Failed to upload video";
    } finally {
      videoStore.setUploading(false);
      videoStore.updateProgress(0);
    }
  }

  function openFileDialog() {
    fileInput?.click();
  }
</script>

<div class="bg-white rounded-2xl p-8 shadow-lg mb-8">
  <h2 class="text-[#111e68] text-2xl font-semibold mb-6">Upload Video</h2>

  {#if $uploadedVideo}
    <div class="flex items-center bg-green-50 p-6 rounded-xl gap-4">
      <div class="text-3xl text-green-600">✓</div>
      <div class="flex-1">
        <strong class="block text-[#111e68] text-lg mb-1">
          {$uploadedVideo.original_filename}
        </strong>
        <p class="text-gray-600 text-sm">
          Duration: {$uploadedVideo.duration.toFixed(1)}s | Resolution: {$uploadedVideo.width}×{$uploadedVideo.height}
          | Frames: {$uploadedVideo.total_frames}
        </p>
      </div>
    </div>
  {:else}
    <div class="text-center">
      <input
        type="file"
        accept={acceptedFormats}
        on:change={handleFileSelect}
        bind:this={fileInput}
        disabled={$isUploading}
        class="hidden"
      />

      {#if !selectedFile}
        <button
          class="bg-[#111e68] text-white font-semibold text-lg py-4 px-8 rounded-xl transition hover:bg-[#1f2e9f] hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed"
          on:click={openFileDialog}
          disabled={$isUploading}
        >
          📁 Select Video File
        </button>

        <p class="text-gray-600 text-sm mt-4">
          Supported: MP4, AVI, MOV, MKV, WEBM (max {maxSizeMB}MB)
        </p>
      {:else}
        <div class="bg-[#f5f7ff] p-6 rounded-xl mt-4 text-left">
          <p class="font-semibold text-[#111e68] text-lg mb-1">
            📹 {selectedFile.name}
          </p>
          <p class="text-gray-600 mb-4">
            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
          </p>

          {#if $isUploading}
            <div class="mt-4">
              <div class="w-full h-8 bg-gray-300 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-[#111e68] to-[#1f2e9f] transition-all"
                  style="width: {$uploadProgress}%"
                ></div>
              </div>
              <span class="text-[#111e68] font-semibold block mt-2">
                {Math.round($uploadProgress)}%
              </span>
            </div>
          {:else}
            <div class="flex gap-4 justify-center mt-4">
              <button
                class="bg-green-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-green-700"
                on:click={handleUpload}
              >
                ⬆️ Upload & Process
              </button>

              <button
                class="bg-red-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-red-700"
                on:click={() => {
                  selectedFile = null;
                  fileInput.value = "";
                }}
              >
                Cancel
              </button>
            </div>
          {/if}
        </div>
      {/if}

      {#if error}
        <div class="bg-red-100 text-red-700 p-4 rounded-lg mt-4">
          ⚠️ {error}
        </div>
      {/if}
    </div>
  {/if}
</div>
