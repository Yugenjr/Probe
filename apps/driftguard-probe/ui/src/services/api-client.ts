import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const tenantId = localStorage.getItem("probe_tenant_id") || "prod-tenant-us-east";
  config.headers.set("X-Tenant-Context", tenantId);
  return config;
});
