import React from 'react';

const LandingPage = () => {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-100 to-indigo-200">
      <div className="text-center px-6">
        <h1 className="text-5xl font-bold mb-4 text-gray-800">Welcome to GTFS Explorer</h1>
        <p className="text-lg text-gray-700 mb-6">
          Find transit routes, nearby stops, maps, and more — all powered by GTFS data.
        </p>
        <a
          href="/search"
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg text-lg hover:bg-indigo-700 transition"
        >
          Start Exploring
        </a>
      </div>
    </div>
  );
};

export default LandingPage;