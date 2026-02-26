import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: '../docs/api_doc.json',
    output: {
      target: 'src/api/generated/index.ts',
      schemas: 'src/api/generated/models',
      mode: 'tags-split',
      client: 'axios',
      mock: true,
      override: {
        mutator: {
          path: './src/api/http-client.ts',
          name: 'apiClient',
        },
      },
    },
  },
})
