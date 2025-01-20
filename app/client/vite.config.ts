import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In prod env, these values are expected from AMP runtime
const prodEnvVar = {
  'import.meta.env.VITE_CDSW_PROJECT': JSON.stringify(process.env.CDSW_PROJECT),
  'import.meta.env.VITE_PROJECT_OWNER': JSON.stringify(process.env.PROJECT_OWNER),
  'import.meta.env.VITE_WORKBENCH_URL': JSON.stringify(`https://${process.env.CDSW_DOMAIN}`),
  'import.meta.env.VITE_HF_TOKEN': JSON.stringify(process.env.hf_token),
  'import.meta.env.VITE_HF_USERNAME': JSON.stringify(process.env.hf_username),
  'import.meta.env.VITE_AMP_URL': JSON.stringify('')
}

export default defineConfig(({ mode }) => {
  return {
    define: (mode === 'production' ? prodEnvVar : {}),
    plugins: [react()],
  };
});

