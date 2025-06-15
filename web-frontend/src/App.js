import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SearchPage from './pages/SearchPage';
import NearbyStops from './pages/NearbyStops';
import MapView from './pages/MapView';
import AboutPage from './pages/AboutPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="/nearby" element={<NearbyStops />} />
      <Route path="/map" element={<MapView />} />
      <Route path="/about" element={<AboutPage />} />
    </Routes>
  );
};

export default App;
