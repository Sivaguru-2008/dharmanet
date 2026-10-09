/** @type {import('next').NextConfig} */
const backend = process.env.BACKEND_URL || "http://127.0.0.1:8005";
const nextConfig = {
  output: "standalone",
  // Browser calls same-origin /api/*; Next proxies to the FastAPI backend (no CORS, no exposed backend URL).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};
export default nextConfig;
