import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [step, setStep] = useState(1)
  
  const [prompt, setPrompt] = useState('')
  const [numSlides, setNumSlides] = useState(5)
  const [style, setStyle] = useState('Современный')
  const [tone, setTone] = useState('Профессиональный')
  const [file, setFile] = useState(null)
  
  const [loading, setLoading] = useState(false)
  const [slides, setSlides] = useState([])
  const [selectedSlide, setSelectedSlide] = useState(0)
  const [imagePreviews, setImagePreviews] = useState({})
  const [uploadingImage, setUploadingImage] = useState(false)
  
  const fileInputRef = useRef(null)

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
      setStep(2)
      setImagePreviews({})
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
    setSlides([])
    setImagePreviews({})
  }

  const updateSlide = (index, field, value) => {
    const updatedSlides = [...slides]
    updatedSlides[index][field] = value
    setSlides(updatedSlides)
  }

  const deleteSlide = (index) => {
    if (slides.length <= 1) {
      alert('Нельзя удалить последний слайд')
      return
    }
    const updatedSlides = slides.filter((_, i) => i !== index)
    setSlides(updatedSlides)
    if (selectedSlide >= updatedSlides.length) {
      setSelectedSlide(updatedSlides.length - 1)
    }
    // Удаляем превью
    const newPreviews = { ...imagePreviews }
    delete newPreviews[index]
    setImagePreviews(newPreviews)
  }

  const addSlide = () => {
    const newSlide = {
      title: `Новый слайд ${slides.length + 1}`,
      content: 'Введите текст для слайда...',
      image_prompt: 'Business presentation slide'
    }
    setSlides([...slides, newSlide])
    setSelectedSlide(slides.length)
  }

  const duplicateSlide = (index) => {
    const newSlide = { ...slides[index] }
    const updatedSlides = [...slides]
    updatedSlides.splice(index + 1, 0, newSlide)
    setSlides(updatedSlides)
  }

  const moveSlide = (index, direction) => {
    if ((direction === -1 && index === 0) || 
        (direction === 1 && index === slides.length - 1)) {
      return
    }
    const updatedSlides = [...slides]
    const temp = updatedSlides[index]
    updatedSlides[index] = updatedSlides[index + direction]
    updatedSlides[index + direction] = temp
    setSlides(updatedSlides)
    setSelectedSlide(index + direction)
  }

  // Загрузка своего изображения
  const handleImageUpload = async (slideIndex, file) => {
    if (!file) return
    
    setUploadingImage(true)
    
    try {
      // Создаем FormData для загрузки файла
      const formData = new FormData()
      formData.append('file', file)
      formData.append('slide_index', slideIndex)
      
      // Отправляем на сервер
      const res = await fetch('http://localhost:8000/upload-image', {
        method: 'POST',
        body: formData
      })
      
      if (!res.ok) throw new Error('Ошибка загрузки изображения')
      
      const data = await res.json()
      
      // Создаем preview для отображения
      const previewUrl = URL.createObjectURL(file)
      setImagePreviews(prev => ({
        ...prev,
        [slideIndex]: previewUrl
      }))
      
      // Обновляем путь к изображению в слайде
      updateSlide(slideIndex, 'image_path', data.file_path)
      
      alert('Изображение загружено!')
    } catch (err) {
      alert('Ошибка: ' + err.message)
    } finally {
      setUploadingImage(false)
    }
  }

  // Удаление изображения
  const removeImage = (slideIndex) => {
    const newPreviews = { ...imagePreviews }
    delete newPreviews[slideIndex]
    setImagePreviews(newPreviews)
    
    // Очищаем путь к изображению
    updateSlide(slideIndex, 'image_path', null)
  }

  // Регенерация изображения через API
  const regenerateImage = async (index) => {
    const slide = slides[index]
    if (!slide.image_prompt) {
      alert('Заполните промпт для изображения')
      return
    }
    
    setUploadingImage(true)
    try {
      const formData = new FormData()
      formData.append('prompt', slide.image_prompt)
      formData.append('slide_index', index)
      
      const res = await fetch('http://localhost:8000/regenerate-image', {
        method: 'POST',
        body: formData
      })
      
      if (!res.ok) throw new Error('Ошибка генерации')
      
      const data = await res.json()
      
      // Обновляем превью (добавляем timestamp чтобы обновить кэш)
      const imageUrl = `http://localhost:8000/${data.file_path}?t=${Date.now()}`
      setImagePreviews(prev => ({
        ...prev,
        [index]: imageUrl
      }))
      
      updateSlide(index, 'image_path', data.file_path)
      
    } catch (err) {
      alert('Ошибка: ' + err.message)
    } finally {
      setUploadingImage(false)
    }
  }

  // Загрузка превью при загрузке страницы
  useEffect(() => {
    if (slides.length > 0) {
      slides.forEach((slide, index) => {
        if (slide.image_path) {
          const url = `http://localhost:8000/${slide.image_path}`
          setImagePreviews(prev => ({
            ...prev,
            [index]: url
          }))
        }
      })
    }
  }, [slides])

  return (
    <div className="app">
      {step === 1 ? (
        <div className="page page1">
          <div className="container">
            <form onSubmit={handleGenerate} className="input-form">
              <div className="form-grid">
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

              <button type="submit" className="create-btn" disabled={loading}>
                {loading ? 'Создание...' : 'Создать презентацию'}
              </button>
            </form>
          </div>
        </div>
      ) : (
        <div className="page page2">
          <div className="container">
            <div className="preview-layout">
              {/* Левая панель: Список слайдов */}
              <div className="slides-panel">
                <div className="panel-header">
                  <h2>Слайды</h2>
                  <button className="add-slide-btn" onClick={addSlide}>
                    + Добавить
                  </button>
                </div>
                <div className="slides-list">
                  {slides.map((slide, index) => (
                    <div
                      key={index}
                      className={`slide-thumbnail ${selectedSlide === index ? 'active' : ''}`}
                      onClick={() => setSelectedSlide(index)}
                    >
                      <div className="slide-number">{index + 1}</div>
                      <div className="slide-preview-text">{slide.title}</div>
                      <div className="slide-actions">
                        <button 
                          className="action-btn" 
                          onClick={(e) => { e.stopPropagation(); duplicateSlide(index); }}
                          title="Дублировать"
                        >
                          📋
                        </button>
                        <button 
                          className="action-btn delete" 
                          onClick={(e) => { e.stopPropagation(); deleteSlide(index); }}
                          title="Удалить"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Правая панель: Редактор */}
              <div className="editor-panel">
                <div className="panel-header">
                  <h2>Редактирование слайда {selectedSlide + 1}</h2>
                  <div className="slide-controls">
                    <button 
                      className="control-btn" 
                      onClick={() => moveSlide(selectedSlide, -1)}
                      disabled={selectedSlide === 0}
                    >
                      ↑ Вверх
                    </button>
                    <button 
                      className="control-btn" 
                      onClick={() => moveSlide(selectedSlide, 1)}
                      disabled={selectedSlide === slides.length - 1}
                    >
                      ↓ Вниз
                    </button>
                  </div>
                </div>

                {slides[selectedSlide] && (
                  <div className="slide-editor">
                    <div className="editor-field">
                      <label>Заголовок слайда</label>
                      <input
                        type="text"
                        value={slides[selectedSlide].title}
                        onChange={(e) => updateSlide(selectedSlide, 'title', e.target.value)}
                        className="title-input"
                      />
                    </div>

                    <div className="editor-field">
                      <label>Содержание слайда</label>
                      <textarea
                        value={slides[selectedSlide].content}
                        onChange={(e) => updateSlide(selectedSlide, 'content', e.target.value)}
                        className="content-textarea"
                        rows={8}
                      />
                    </div>

                    <div className="editor-field">
                      <label>Промпт для изображения</label>
                      <input
                        type="text"
                        value={slides[selectedSlide].image_prompt || ''}
                        onChange={(e) => updateSlide(selectedSlide, 'image_prompt', e.target.value)}
                        placeholder="Опишите изображение для этого слайда..."
                      />
                    </div>

                    {/* Блок управления изображением */}
                    <div className="editor-field image-editor">
                      <label>Изображение слайда</label>
                      
                      {imagePreviews[selectedSlide] ? (
                        <div className="image-preview-container">
                          <img 
                            src={imagePreviews[selectedSlide]} 
                            alt={`Slide ${selectedSlide + 1}`}
                            className="uploaded-image"
                          />
                          <div className="image-actions">
                            <button 
                              className="btn-secondary"
                              onClick={() => fileInputRef.current?.click()}
                              disabled={uploadingImage}
                            >
                              🔄 Заменить
                            </button>
                            <button 
                              className="btn-danger"
                              onClick={() => removeImage(selectedSlide)}
                              disabled={uploadingImage}
                            >
                              🗑️ Удалить
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="image-upload-placeholder">
                          <p>Изображение не загружено</p>
                          <div className="upload-options">
                            <button 
                              className="btn-primary"
                              onClick={() => fileInputRef.current?.click()}
                              disabled={uploadingImage}
                            >
                              {uploadingImage ? '⏳ Загрузка...' : '📤 Загрузить своё'}
                            </button>
                            <button 
                              className="btn-secondary"
                              onClick={() => regenerateImage(selectedSlide)}
                              disabled={uploadingImage || !slides[selectedSlide].image_prompt}
                            >
                              🎨 Сгенерировать AI
                            </button>
                          </div>
                        </div>
                      )}
                      
                      {/* Скрытый input для загрузки файла */}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={(e) => {
                          if (e.target.files[0]) {
                            handleImageUpload(selectedSlide, e.target.files[0])
                          }
                        }}
                      />
                    </div>
                  </div>
                )}

                <div className="editor-actions">
                  <button className="download-btn" onClick={handleDownload}>
                    💾 Скачать презентацию
                  </button>
                  <button className="back-btn" onClick={handleBack}>
                    ← Создать новую
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App