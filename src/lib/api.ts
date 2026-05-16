import { clearSession, getToken } from "@/lib/auth-storage";

/** Use empty string in dev to leverage Vite proxy; set VITE_API_URL in production */
const API_BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = RequestInit & {
  auth?: boolean;
  body?: unknown;
};

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg || "").join(", ");
    }
    return data.message || response.statusText;
  } catch {
    return response.statusText || "Request failed";
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { auth = false, body, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    ...(customHeaders as Record<string, string>),
  };

  if (body !== undefined && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getToken();
    if (!token) {
      throw new ApiError("Not authenticated", 401);
    }
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers,
    body:
      body instanceof FormData
        ? body
        : body !== undefined
          ? JSON.stringify(body)
          : undefined,
  });

  if (response.status === 401) {
    clearSession();
  }

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export { API_BASE };
