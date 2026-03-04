import axios, { type AxiosRequestConfig } from 'axios'

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = httpClient

export const orvalMutator = async <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig
) => {
  const response = await httpClient({
    ...config,
    ...options,
  })

  return response.data as T
}

export type ApiClient = typeof apiClient

