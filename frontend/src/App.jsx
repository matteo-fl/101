import { useState } from 'react'
import './App.css'

function App() {
  const [step, setStep] = useState(1) // 1 - input, 2 - results
  
  const [prompt, setPrompt] = useState('')
  const [numSlides, setNumSlides] = useState(5)
  const [style, setStyle] = useState('Современный')
  const [tone, setTone] = useState('Профессиональный')
  const [file, setFile] = useState(null)
  
  const [loading, setLoading] = useState(false)
  const [slides, setSlides] = useState([])
  const [selectedSlide, setSelectedSlide] = useState(0)

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)

    const formData = new FormData()
    formData.append('prompt', prompt)
    formData.append('num_slides', numSlides)
    formData.append('style', style)
    formData.append('tone', tone)
    if (file) formData.append('file', file)

    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      
      if (!res.ok) throw new Error(data.error || 'Ошибка сервера')
      setSlides(data.slides)
      setStep(2) // Переход на страницу результатов
    } catch (err) {
      alert('Ошибка: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const res = await fetch('http://localhost:8000/download')
      if (!res.ok) throw new Error('Файл не найден')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'presentation.pptx'
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (err) {
      alert('Ошибка скачивания: ' + err.message)
    }
  }

  const handleBack = () => {
    setStep(1)
    setPrompt('')
    setFile(null)
  }

  return (
    <div className="app">
      {step === 1 ? (
        // СТРАНИЦА 1: Ввод данных
        <div className="page page1">
          <div className="container">
            <form onSubmit={handleGenerate} className="input-form">
              <div className="form-grid">
                {/* Колонка 1: Введите запрос */}
                <div className="column">
                  <h2>Введите запрос</h2>
                  <textarea
                    placeholder="Опишите тему презентации..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    required
                    rows={10}
                  />
                </div>

                {/* Колонка 2: Прикрепите файл */}
                <div className="column">
                  <h2>Прикрепите файл</h2>
                  <div className="file-upload-area">
                    <input
                      type="file"
                      onChange={(e) => setFile(e.target.files[0])}
                      accept=".pdf,.docx"
                      id="file-input"
                    />
                    <label htmlFor="file-input" className="file-label">
                      <div className="paperclip-icon">📎</div>
                      <div className="file-text">PDF/DOCX</div>
                      {file && <div className="file-name">{file.name}</div>}
                    </label>
                  </div>
                </div>

                {/* Колонка 3: Настройки */}
                <div className="column">
                  <h2>Настройки</h2>
                  <div className="settings">
                    <div className="setting-item">
                      <label>Количество слайдов</label>
                      <input
                        type="number"
                        min="1"
                        max="20"
                        value={numSlides}
                        onChange={(e) => setNumSlides(Number(e.target.value))}
                      />
                    </div>
                    <div className="setting-item">
                      <label>Стиль оформления</label>
                      <select value={style} onChange={(e) => setStyle(e.target.value)}>
                        <option>Современный</option>
                        <option>Корпоративный</option>
                        <option>Минимализм</option>
                        <option>Креативный</option>
                      </select>
                    </div>
                    <div className="setting-item">
                      <label>Тон повествования</label>
                      <select value={tone} onChange={(e) => setTone(e.target.value)}>
                        <option>Профессиональный</option>
                        <option>Дружелюбный</option>
                        <option>Академический</option>
                        <option>Деловой</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Кнопка создать */}
              <button type="submit" className="create-btn" disabled={loading}>
                {loading ? 'Создание...' : 'Создать презентацию'}
              </button>
            </form>
          </div>
        </div>
      ) : (
        // СТРАНИЦА 2: Предпросмотр
        <div className="page page2">
          <div className="container">
            <div className="preview-layout">
              {/* Левая колонка: Слайды */}
              <div className="slides-panel">
                <h2>Слайды</h2>
                <div className="slides-list">
                  {slides.map((slide, index) => (
                    <div
                      key={index}
                      className={`slide-thumbnail ${selectedSlide === index ? 'active' : ''}`}
                      onClick={() => setSelectedSlide(index)}
                    >
                      <div className="slide-number">{index + 1}</div>
                      <div className="slide-preview-text">{slide.title}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Правая колонка: Предпросмотр */}
              <div className="preview-panel">
                <h2>Предпросмотр</h2>
                {slides[selectedSlide] && (
                  <div className="slide-preview">
                    <div className="preview-header">{slides[selectedSlide].title}</div>
                    <div className="preview-content">{slides[selectedSlide].content}</div>
                  </div>
                )}
                
                {/* Кнопка скачать */}
                <button className="download-btn" onClick={handleDownload}>
                  Скачать презентацию
                </button>
                
                {/* Кнопка назад */}
                <button className="back-btn" onClick={handleBack}>
                  ← Создать новую
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App