import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["heroai.local"],
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/assets/**",
      },
      {
        protocol: "http",
        hostname: "heroai.local",
        port: "8000",
        pathname: "/assets/**",
      },
    ],
  },
};

export default nextConfig;
