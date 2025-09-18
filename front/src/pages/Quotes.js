import React, { useState, useEffect } from 'react';
import './Quotes.css';

function Quotes() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedFuelType, setSelectedFuelType] = useState('LSMGO');

    useEffect(() => {
        fetch(`${process.env.REACT_APP_API_URL}/api/quotes`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Сортируем данные от ранней даты к поздней для каждого типа котировок
                const sortedData = {};
                Object.keys(data).forEach(fuelType => {
                    if (data[fuelType] && Array.isArray(data[fuelType])) {
                        sortedData[fuelType] = data[fuelType]
                            .slice()
                            .sort((a, b) => new Date(b.date) - new Date(a.date));
                    }
                });
                setData(sortedData);
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching quotes data:", error);
                setError(error);
                setLoading(false);
            });
    }, []);

    const handleFuelTypeChange = (event) => {
        setSelectedFuelType(event.target.value);
    };

    if (loading) return <div className="loading">Загрузка котировок...</div>;
    if (error) return <div className="error">Ошибка: {error.message}</div>;
    if (!data) return <div>Нет данных</div>;

    const availableFuelTypes = Object.keys(data).filter(fuelType => 
        data[fuelType] && data[fuelType].length > 0
    );

    return (
        <div className="quotes-container">
            <div className="quotes-header">
                <h1>Котировки топлива</h1>
                {availableFuelTypes.length > 0 && (
                    <div className="fuel-type-selector">
                        <label htmlFor="fuelType">Выберите тип топлива: </label>
                        <select 
                            id="fuelType"
                            value={selectedFuelType} 
                            onChange={handleFuelTypeChange}
                        >
                            {availableFuelTypes.map(fuelType => (
                                <option key={fuelType} value={fuelType}>
                                    {fuelType}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>
            
            {data[selectedFuelType] && data[selectedFuelType].length > 0 ? (
                <div className="quotes-table">
                    <h2>{selectedFuelType}</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th>Цена ($/т)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data[selectedFuelType].map((quote, index) => (
                                <tr key={index}>
                                    <td>{quote.date}</td>
                                    <td>{quote.price.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="no-data">
                    Нет данных для {selectedFuelType}
                </div>
            )}
        </div>
    );
}

export default Quotes;