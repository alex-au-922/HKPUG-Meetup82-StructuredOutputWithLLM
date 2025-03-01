/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_NATIVE_BLOCKING_API: string
    readonly VITE_INSTRUCTOR_STREAMING_API: string
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }