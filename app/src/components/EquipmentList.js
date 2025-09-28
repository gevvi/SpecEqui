import React, { useState, useMemo } from 'react';
import EquipmentItem from './EquipmentItem';

function EquipmentList({ equipment }) {
  // 1. Состояние «по какому ключу сортировать»
  const [sortKey, setSortKey] = useState('title');
  // 2. Пересчитываем отсортированный массив только если изменился `equipment` или `sortKey`
  const sortedEquipment = useMemo(() => {
    // Создаём копию, чтобы не мутировать пропсы
    let sorted = [...equipment];
    if (sortKey === 'title') {
      sorted.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortKey === 'priceAsc') {
      sorted.sort((a, b) => a.price_per_hour - b.price_per_hour);
    } else if (sortKey === 'priceDesc') {
      sorted.sort((a, b) => b.price_per_hour - a.price_per_hour);
    }
    return sorted;
  }, [equipment, sortKey]);
  // ↑ useMemo вернёт «запомненный» результат, если зависимости не изменились.

  // 3. Пагинация (будем показывать по 3 единицы техники на странице для примера)
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 3;
  // Сколько всего страниц:
  const totalPages = Math.ceil(sortedEquipment.length / itemsPerPage);

  // Функция для генерации массива номеров страниц,
  // но ограничим только соседними номерами от текущей страницы (по 1 слева/справа)
  const getPageRange = () => {
    const delta = 1; // показать по одному номеру слева и справа
    const range = [];
    for (
      let num = Math.max(1, currentPage - delta);
      num <= Math.min(totalPages, currentPage + delta);
      num++
    ) {
      range.push(num);
    }
    return range;
  };

  // 4. Выбираем единицы техники, которые должны отображаться на текущей странице:
  const startIdx = (currentPage - 1) * itemsPerPage;
  const endIdx = startIdx + itemsPerPage;
  const equipmentToDisplay = sortedEquipment.slice(startIdx, endIdx);

  return (
    <div>
      {/* 3.1. Селект для смены порядка сортировки */}
      <div className="sort-container">
        <label>Сортировать по: </label>
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
          <option value="title">Название (A→Z)</option>
          <option value="priceAsc">Цена за час (возр.→убыв.)</option>
          <option value="priceDesc">Цена за час (убыв.→возр.)</option>
        </select>
      </div>

      {/* 3.2. Здесь проходимся по equipmentToDisplay и рендерим EquipmentItem с ключом key */}
      <ul className="list-articles">
        {equipmentToDisplay.map((equipment) => (
          <EquipmentItem key={equipment.id} equipment={equipment} />
        ))}
      </ul>

      {/* 3.3. Постраничная навигация: показываем только если totalPages > 1 */}
      {totalPages > 1 && (
        <nav className="pagination-nav">
          {/* Кнопка «Prev», если мы не на первой странице */}
          {currentPage > 1 && (
            <button onClick={() => setCurrentPage((prev) => prev - 1)}>
              Prev
            </button>
          )}

          {/* Перебираем номера страниц из getPageRange() */}
          {getPageRange().map((num) =>
            num === currentPage ? (
              // Если номер == текущая страница, просто текст (без ссылки)
              <span key={num} className="page-number active">
                {num}
              </span>
            ) : (
              // Для остальных — кнопка, которая ставит currentPage=num
              <button key={num} onClick={() => setCurrentPage(num)}>
                {num}
              </button>
            )
          )}

          {/* Кнопка «Next», если мы не на последней странице */}
          {currentPage < totalPages && (
            <button onClick={() => setCurrentPage((prev) => prev + 1)}>
              Next
            </button>
          )}
        </nav>
      )}
    </div>
  );
}

export default EquipmentList;
