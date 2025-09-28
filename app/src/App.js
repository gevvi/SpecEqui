import React, { useState } from 'react';
import EquipmentList from './components/EquipmentList';
import EquipmentForm from './components/EquipmentForm';
import './components/styles.css';

function App() {
  // 2.1. Исходные тестовые данные: массив объектов «спецтехника»
  // Это позволит сразу проверить сортировку/пагинацию. В реальном приложении эти данные шли бы с сервера.
  const [equipment, setEquipment] = useState([
    { id: 1, title: 'Экскаватор JCB 220', description: 'Надёжный экскаватор для земляных работ.', manufacturer: 'JCB', price_per_hour: 2500 },
    { id: 2, title: 'Бульдозер CAT D6T', description: 'Мощный бульдозер для планировки.', manufacturer: 'Caterpillar', price_per_hour: 2800 },
    { id: 3, title: 'Кран Liebherr LTM 1200', description: 'Мобильный кран высокой грузоподъёмности.', manufacturer: 'Liebherr', price_per_hour: 4000 },
    { id: 4, title: 'Манипулятор UNIC URW-376', description: 'Грузовой манипулятор для погрузки.', manufacturer: 'UNIC', price_per_hour: 1800 },
    { id: 5, title: 'Газель Next', description: 'Лёгкий грузовик для перевозок.', manufacturer: 'ГАЗ', price_per_hour: 1200 },
    { id: 6, title: 'Бетономешалка SICOMA', description: 'Автобетоносмеситель для строительства.', manufacturer: 'SICOMA', price_per_hour: 2200 },
  ]);

  // 2.2. Функция для добавления новой единицы техники в «локальный стейт»
  const handleAddEquipment = (newEquipment) => {
    setEquipment((prevEquipment) => [...prevEquipment, newEquipment]);
  };

  return (
    <div className="App">
      <h1 style={{ textAlign: 'center' }}>Специальное оборудование</h1>

      {/* 4.1. Рендерим компонент EquipmentForm и передаём ему колбэк onAddEquipment */}
      <EquipmentForm onAddEquipment={handleAddEquipment} />

      {/* 3.1. Рендерим компонент EquipmentList, передаём проп equipment */}
      <EquipmentList equipment={equipment} />
    </div>
  );
}

export default App;
