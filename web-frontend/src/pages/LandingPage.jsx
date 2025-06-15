export default function LandingPage() {
  return (
    <div className="relative h-screen bg-gradient-to-br from-blue-900 to-sky-400 text-white">
      {/* Navbar */}
      <nav className="absolute top-0 left-0 w-full flex items-center justify-between px-8 py-4 bg-transparent z-10">
        {/* Left side: Auth links */}
        <div>
          <img src="/static/logo.png" alt="GTFS Explorer" className="h-10 w-auto" />
        </div>
        
        {/* Right side: Logo */}
        <div className="flex space-x-4">
          <a href="/signin" className="text-white font-medium hover:underline">
            Sign In
          </a>
          <a href="/signup" className="text-white font-medium hover:underline">
            Sign Up
          </a>
        </div>
        
      </nav>

      {/* Main Content */}
      <div className="flex items-center justify-center h-full">
        <div className="text-center px-6">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">Welcome to GTFS Explorer</h1>
          <p className="text-lg md:text-xl mb-0">Find routes, explore stops, and plan your trips seamlessly</p>
          <p className="text-lg md:text-xl mb-6">within Nairobi.</p>
          <div className="space-x-4">
            <a
              href="/search"
              className="bg-white text-blue-800 font-semibold px-5 py-2 rounded shadow hover:bg-gray-100 transition"
            >
              Search Routes
            </a>
            <a
              href="/nearby"
              className="bg-white text-blue-800 font-semibold px-5 py-2 rounded shadow hover:bg-gray-100 transition"
            >
              Nearby Stops
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

