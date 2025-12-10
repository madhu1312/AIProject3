import { Link, useLocation } from 'react-router-dom';
import { FileText, Home, PlusCircle } from 'lucide-react';

export const Navbar = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-gray-900 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl">
              <FileText className="text-indigo-500" />
              <span>CMS</span>
            </Link>
            <div className="ml-10 flex items-baseline space-x-4">
              <Link
                to="/"
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <Home size={16} />
                Articles
              </Link>
            </div>
          </div>
          <div>
            <Link
              to="/articles/new"
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              <PlusCircle size={16} />
              Create Document
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
