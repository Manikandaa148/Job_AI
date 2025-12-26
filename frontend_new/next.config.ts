import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: isProd ? '/Job_AI' : '',
  assetPrefix: isProd ? '/Job_AI/' : '',
  trailingSlash: true,
};

export default nextConfig;
