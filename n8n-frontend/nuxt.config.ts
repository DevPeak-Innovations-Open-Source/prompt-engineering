// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  app: {
    baseURL: "/prompt-engineering/"
  },
  devtools: { enabled: true },
  modules: ['@nuxt/icon', '@nuxt/image', '@nuxtjs/tailwindcss'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiUrl: 'http://localhost:8000'
    }
  }
})