import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components';
import {
  ArticleList,
  ArticleCreate,
  ArticleEdit,
  ArticleView,
  ArticlePreview,
} from './pages';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900">
        <Routes>
          {/* Preview route without navbar */}
          <Route path="/preview/:slug" element={<ArticlePreview />} />
          
          {/* CMS routes with navbar */}
          <Route
            path="*"
            element={
              <>
                <Navbar />
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                  <Routes>
                    <Route path="/" element={<ArticleList />} />
                    <Route path="/articles/new" element={<ArticleCreate />} />
                    <Route path="/articles/:id" element={<ArticleView />} />
                    <Route path="/articles/:id/edit" element={<ArticleEdit />} />
                  </Routes>
                </main>
              </>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
