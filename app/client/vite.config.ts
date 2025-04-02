import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In prod env, these values are expected from AMP runtime
const prodEnvVar = {
  'import.meta.env.VITE_CDSW_PROJECT': JSON.stringify(process.env.CDSW_PROJECT),
  'import.meta.env.VITE_CDSW_PROJECT_URL': JSON.stringify(process.env.CDSW_PROJECT_URL),
  'import.meta.env.VITE_PROJECT_OWNER': JSON.stringify(process.env.PROJECT_OWNER),
  'import.meta.env.VITE_WORKBENCH_URL': JSON.stringify(`https://${process.env.CDSW_DOMAIN}`),
  'import.meta.env.VITE_HF_TOKEN': JSON.stringify(process.env.hf_token),
  'import.meta.env.VITE_HF_USERNAME': JSON.stringify(process.env.hf_username),
  'import.meta.env.VITE_AMP_URL': JSON.stringify(''),
  'import.meta.env.VITE_CDSW_API_URL': JSON.stringify(process.env.CDSW_API_URL),
  'import.meta.env.VITE_CDSW_DOMAIN': JSON.stringify(process.env.CDSW_DOMAIN),
  'import.meta.env.VITE_IS_COMPOSABLE': JSON.stringify(process.env.IS_COMPOSABLE),
  'import.meta.env.VITE_CDSW_APIV2_KEY': JSON.stringify(process.env.CDSW_APIV2_KEY),
}

export default defineConfig(({ mode }) => {
  return {
    define: (mode === 'production' ? prodEnvVar : {}),
    plugins: [react()],
    test: {
      environment: 'jsdom',
      globals: true
    }
 };
});