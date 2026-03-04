import React, { useState } from "react";

const ShipInventory = ({ shipName, cargoCapacity }) => {
  const [items, setItems] = useState([]);

  return (
    <div className="inventory-panel">
      <h2>{shipName} Payload</h2>

      <ul>
        {items.map((item, index) => {
          return (
            <li key={index}>
              {item.name}-{item.weight}kg
            </li>
          );
        })}
      </ul>

      <button
        onClick={() => {
          console.log("Jettison cargo");
          console.log("Current cargo items:", items);
        }}
      >
        Empty Hold
      </button>
    </div>
  );
};

export default ShipInventory;
