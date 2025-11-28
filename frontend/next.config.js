/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow API proxy for local development only
  // In production, use Vercel rewrites (vercel.json) or NEXT_PUBLIC_API_URL env var
  async rewrites() {
    // Only use rewrites in development or if API URL is explicitly set
    const apiUrl = process.env.NEXT_PUBLIC_API_URL
    if (apiUrl || process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: `${apiUrl || 'http://127.0.0.1:8000'}/api/:path*`,
        },
      ]
    }
    return []
  },
};

module.exports = nextConfig;

