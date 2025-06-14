import React from 'react';

export default function LandingPage() {
  return (
    <div className="h-screen w-screen bg-gradient-to-br from-blue-600 to-green-400 text-white flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl md:text-6xl font-bold mb-4">GTFS Web App</h1>
      <p className="text-lg md:text-2xl text-center max-w-xl mb-6">
        Explore transit routes, find nearby stops, and search public transport data with ease.
      </p>
      <a href="/search" className="px-6 py-3 bg-white text-blue-600 font-semibold rounded-full shadow-lg hover:bg-gray-100 transition">
        Get Started
      </a>
    </div>
  );
}