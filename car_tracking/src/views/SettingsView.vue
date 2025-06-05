<template>
  <div class="file-uploader">
    <div 
      class="dropzone"
      @click="openFileDialog"
      @dragover.prevent="setDragover(true)"
      @dragleave.prevent="setDragover(false)"
      @drop.prevent="handleDrop"
      :class="{ 'dragover': isDragover }"
    >
      <div class="upload-content">
        <i class="pi pi-cloud-upload upload-icon"></i>
        <p class="upload-text">drag or select files</p>
        <p class="formats-text">supported formats: mp4, webm, mp3, ogg, opus, wav, m4a</p>
        <input 
          ref="fileInput"
          type="file"
          @change="handleFileSelect"
          multiple
          accept=".mp4,.webm,.mp3,.ogg,.opus,.wav,.m4a"
          class="file-input"
        >
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isDragover: false
    }
  },
  methods: {
    openFileDialog() {
      this.$refs.fileInput.click()
    },
    setDragover(state) {
      this.isDragover = state
    },
    handleDrop(e) {
      this.setDragover(false)
      this.processFiles(e.dataTransfer.files)
    },
    handleFileSelect(e) {
      this.processFiles(e.target.files)
    },
    processFiles(files) {
      if (files.length) {
        this.$emit('files-selected', Array.from(files))
      }
    }
  }
}
</script>

<style scoped>
.file-uploader {
  max-width: 400px;
  margin: 0 auto;
}

.dropzone {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 2rem;
  transition: all 0.3s ease;
  cursor: pointer;
  background-color: #f9fafb;
  text-align: center;
}

.dropzone:hover {
  border-color: #9ca3af;
  background-color: #f3f4f6;
}

.dropzone.dragover {
  border-color: #3b82f6;
  background-color: #e0e7ff;
}

.upload-content {
  color: #4b5563;
}

.upload-icon {
  font-size: 2.5rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0.5rem 0;
  color: #111827;
}

.formats-text {
  font-size: 0.85rem;
  margin: 0.5rem 0 0;
  color: #6b7280;
}

.file-input {
  display: none;
}
</style>