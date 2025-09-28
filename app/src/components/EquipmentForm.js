import React, { useState } from 'react';

function EquipmentForm({ onAddEquipment }) {
  // 1. Состояние каждого поля формы и ошибок
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price_per_hour, setPricePerHour] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [errors, setErrors] = useState({});

  // 2. Функция validate() проверяет данные формы перед отправкой
  const validate = () => {
    const errs = {};
    // Проверяем, что title не пустое
    if (!title.trim()) errs.title = 'Название не может быть пустым';
    // Проверяем, что manufacturer не пустое
    if (!manufacturer.trim()) errs.manufacturer = 'Производитель не может быть пустым';
    // Проверяем, что price_per_hour — это число ≥ 0
    if (price_per_hour === '' || isNaN(price_per_hour) || Number(price_per_hour) < 0) {
      errs.price_per_hour = 'Цена за час должна быть числом ≥ 0';
    }
    return errs; // вернёт объект вида { title: '...', price_per_hour: '...' } либо {}
  };

  // 3. handleSubmit вызывается при нажатии «Submit»
  const handleSubmit = (e) => {
    e.preventDefault(); // предотвратить перезагрузку страницы

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      // Если есть ошибки, сохраняем в состояние и выходим
      setErrors(validationErrors);
      return;
    }

    // 4. Если валидация успешна — формируем объект новой единицы техники
    const newEquipment = {
      id: Date.now(),              // генерируем простой уникальный id
      title: title.trim(),
      description: description.trim(),
      manufacturer: manufacturer.trim(),
      price_per_hour: Number(price_per_hour),
    };
    onAddEquipment(newEquipment); // поднимаем состояние наверх (из App.js)

    // 5. Сбрасываем форму после успешного добавления
    setTitle('');
    setDescription('');
    setManufacturer('');
    setPricePerHour('');
    setErrors({});
  };

  return (
    <form className="equipment-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Название техники:</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          // Если валидация показала ошибку для title, добавляем класс 'invalid'
          className={errors.title ? 'invalid' : ''}
        />
        {/* Если ошибка по title есть — показываем текст снизу */}
        {errors.title && <div className="error-text">{errors.title}</div>}
      </div>

      <div className="form-group">
        <label>Описание:</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Производитель:</label>
        <input
          type="text"
          value={manufacturer}
          onChange={(e) => setManufacturer(e.target.value)}
          className={errors.manufacturer ? 'invalid' : ''}
        />
        {errors.manufacturer && <div className="error-text">{errors.manufacturer}</div>}
      </div>

      <div className="form-group">
        <label>Цена за час (₽):</label>
        <input
          type="number"
          value={price_per_hour}
          onChange={(e) => setPricePerHour(e.target.value)}
          className={errors.price_per_hour ? 'invalid' : ''}
        />
        {errors.price_per_hour && <div className="error-text">{errors.price_per_hour}</div>}
      </div>

      <button type="submit" className="btn-submit">
        Добавить технику
      </button>
    </form>
  );
}

export default EquipmentForm;
