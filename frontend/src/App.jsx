// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Header from './components/Header';
import GenerationForm from './components/GenerationForm';
import SlidesPreview from './components/SlidesPreview';
import Loader from './components/Loader';
import { generatePresentation } from './services/api';
import styles from './App.module.scss';

const AppContent = () => {
  const [loading, setLoading] = useState(false);
  const [slides, setSlides] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleGenerate = async (request) => {
    setLoading(true);
    setError(null);

    try {
      const response = await generatePresentation(request);
      setSlides(response.slides);
      setSessionId(response.session_id);

      // 👈 Переход на страницу редактора
      navigate('/editor', {
        state: { slides: response.slides, sessionId: response.session_id }
      });
    } catch (err) {
      console.error('Generation error:', err);
      setError(err.response?.data?.detail || 'Ошибка при генерации презентации');
      setTimeout(() => setError(null), 5000);
      setLoading(false);
    }
  };

  return (
    <div className={styles.app}>
      <Header />
      <main className={styles.main}>
        {error && (
          <div className={styles.errorToast}>
            {error}
          </div>
        )}

        <Routes>
          <Route path="/" element={
            !loading ? (
              <GenerationForm onSubmit={handleGenerate} loading={loading} />
            ) : (
              <Loader message="ИИ анализирует запрос и создает презентацию..." />
            )
          } />
          <Route path="/editor" element={
            <SlidesPreview
              slides={slides}
              sessionId={sessionId}
              onSlidesUpdate={(updatedSlides) => setSlides(updatedSlides)}
            />
          } />
        </Routes>
      </main>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;