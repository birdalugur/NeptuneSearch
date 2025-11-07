<!--
Video dosyası yükleme ve upload progress gösterimi için kullanılır.
-->

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

  /**
   * Dosya seçildiğinde çağrılır
   */
  function handleFileSelect(event) {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    // Dosya boyutu kontrolü
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      error = `Video file is too large. Maximum size is ${maxSizeMB}MB`;
      selectedFile = null;
      return;
    }

    selectedFile = file;
    error = null;
  }

  /**
   * Video upload işlemini başlatır
   */
  async function handleUpload() {
    if (!selectedFile) {
      return;
    }

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

        // Reset form
        selectedFile = null;
        if (fileInput) {
          fileInput.value = "";
        }
      } else {
        error = response.message || "Upload failed";
      }
    } catch (err) {
      console.error("Upload error:", err);
      error = err.message || "Failed to upload video";
    } finally {
      videoStore.setUploading(false);
      videoStore.updateProgress(0);
    }
  }

  /**
   * Dosya seçim dialogunu açar
   */
  function openFileDialog() {
    fileInput?.click();
  }
</script>

<div class="uploader-container">
  <h2>Upload Video</h2>

  {#if $uploadedVideo}
    <div class="video-info">
      <div class="info-icon">✓</div>
      <div class="info-content">
        <strong>{$uploadedVideo.original_filename}</strong>
        <p>
          Duration: {$uploadedVideo.duration.toFixed(1)}s | Resolution: {$uploadedVideo.width}×{$uploadedVideo.height}
          | Frames: {$uploadedVideo.total_frames}
        </p>
      </div>
    </div>
  {:else}
    <div class="upload-area">
      <input
        type="file"
        accept={acceptedFormats}
        on:change={handleFileSelect}
        bind:this={fileInput}
        disabled={$isUploading}
        style="display: none;"
      />

      {#if !selectedFile}
        <button
          class="select-btn"
          on:click={openFileDialog}
          disabled={$isUploading}
        >
          📁 Select Video File
        </button>
        <p class="hint">
          Supported formats: MP4, AVI, MOV, MKV, WEBM (max {maxSizeMB}MB)
        </p>
      {:else}
        <div class="selected-file">
          <p class="file-name">📹 {selectedFile.name}</p>
          <p class="file-size">
            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
          </p>

          {#if $isUploading}
            <div class="progress-container">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  style="width: {$uploadProgress}%"
                ></div>
              </div>
              <span class="progress-text">{Math.round($uploadProgress)}%</span>
            </div>
          {:else}
            <div class="button-group">
              <button class="upload-btn" on:click={handleUpload}>
                ⬆️ Upload & Process
              </button>
              <button
                class="cancel-btn"
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
        <div class="error-message">
          ⚠️ {error}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .uploader-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
  }

  h2 {
    margin: 0 0 1.5rem 0;
    color: #111e68;
    font-size: 1.5rem;
  }

  .upload-area {
    text-align: center;
  }

  .select-btn {
    background-color: #111e68;
    color: white;
    font-weight: 600;
    font-size: 1.1rem;
    padding: 1rem 2rem;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    transition:
      background-color 0.3s ease,
      transform 0.2s ease;
  }

  .select-btn:hover:not(:disabled) {
    background-color: #1f2e9f;
    transform: translateY(-2px);
  }

  .select-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .hint {
    margin-top: 1rem;
    color: #666;
    font-size: 0.9rem;
  }

  .selected-file {
    background: #f5f7ff;
    padding: 1.5rem;
    border-radius: 10px;
    margin-top: 1rem;
  }

  .file-name {
    font-weight: 600;
    color: #111e68;
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
  }

  .file-size {
    color: #666;
    margin: 0 0 1rem 0;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 1rem;
  }

  .upload-btn {
    background-color: #28a745;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }

  .upload-btn:hover {
    background-color: #218838;
  }

  .cancel-btn {
    background-color: #dc3545;
    color: white;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }

  .cancel-btn:hover {
    background-color: #c82333;
  }

  .progress-container {
    margin-top: 1rem;
  }

  .progress-bar {
    width: 100%;
    height: 30px;
    background-color: #e0e0e0;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #111e68, #1f2e9f);
    transition: width 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
  }

  .progress-text {
    display: block;
    margin-top: 0.5rem;
    font-weight: 600;
    color: #111e68;
  }

  .error-message {
    background-color: #fee;
    color: #c00;
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1rem;
  }

  .video-info {
    display: flex;
    align-items: center;
    background: #e8f5e9;
    padding: 1.5rem;
    border-radius: 10px;
    gap: 1rem;
  }

  .info-icon {
    font-size: 2rem;
    color: #28a745;
    flex-shrink: 0;
  }

  .info-content {
    flex: 1;
  }

  .info-content strong {
    display: block;
    color: #111e68;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
  }

  .info-content p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
</style>
