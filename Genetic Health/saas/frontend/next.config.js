/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow Clerk's hosted image domains
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'img.clerk.com' },
      { protocol: 'https', hostname: 'images.clerk.dev' },
    ],
  },
};

module.exports = nextConfig;
