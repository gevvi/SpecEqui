import React from 'react';

function EquipmentItem({ equipment }) {
  return (
    <li className="equipment-item">
      <h3>{equipment.title}</h3>
      <p>{equipment.description}</p>
      <p>Производитель: {equipment.manufacturer}</p>
      <p>Цена за час: {equipment.price_per_hour} ₽</p>
    </li>
  );
}

export default EquipmentItem;
