import type { NextConfig } from "next";

// In development, /api is proxied to the local FastAPI server (uvicorn on :8000).
// On Vercel, the top-level vercel.json routes /api to the Python service instead.
const API_DEV = process.env.NODUS_API_DEV ?? "http://127.0.0.1:8010";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return [{ source: "/api/:path*", destination: `${API_DEV}/api/:path*` }];
  },
};

export default nextConfig;
