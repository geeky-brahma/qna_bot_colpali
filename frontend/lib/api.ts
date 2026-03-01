import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 100000, // 100 second timeout for inference
});

export interface QueryRequest {
  query: string;
  subject: string;
  userEmail: string;
}

export interface QueryResponse {
  answer: string;
  sourcePages: number[];
  cached: boolean;
  responseTime: number;
}

export async function queryAPI(request: QueryRequest): Promise<QueryResponse> {
  try {
    const response = await apiClient.post<QueryResponse>(
      "/api/query",
      request
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.message ||
          error.message ||
          "Failed to query API"
      );
    }
    throw error;
  }
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await apiClient.get("/health");
    return response.status === 200;
  } catch {
    return false;
  }
}
