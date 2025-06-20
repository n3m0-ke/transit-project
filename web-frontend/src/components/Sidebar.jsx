export default function Sidebar({ icons, activePanel, setActivePanel, isOpen, setIsOpen }) {
  return (
    <div className="w-16 bg-white text-gray-800 shadow-lg z-10">
      <div className="flex flex-col h-full items-center">
        <button
          className="p-4 hover:bg-gray-200"
          onClick={() => setIsOpen(!isOpen)}
        >
          {icons.menu || <span>=</span>}
        </button>

        <nav className="flex flex-col space-y-2 mt-2">
          {Object.entries(icons).filter(([key]) => key !== "menu").map(([panel, icon]) => (
            <button
              key={panel}
              onClick={() =>
                setActivePanel((prev) => (prev === panel ? null : panel))
              }
              className={`$ {
                activePanel === panel ? "bg-gray-200" : "hover:bg-gray-100"
              } p-2 rounded flex items-center justify-center`}
              title={panel.charAt(0).toUpperCase() + panel.slice(1)}
            >
              {icon}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}
