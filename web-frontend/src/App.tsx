import { Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import SearchPage from './pages/SearchPage';
import NearbyStopsPage from './pages/NearbyStopsPage';
import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="/nearby" element={<NearbyStopsPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}