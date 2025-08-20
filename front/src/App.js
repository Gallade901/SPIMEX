import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [purchaseVolume, setPurchaseVolume] = useState(null);
    const [sma10, setSma10] = useState(null);
    const [dailyPrices, setDailyPrices] = useState(null);
    const [monthlyPrice, setMonthlyPrice] = useState(null);
    const [minnAvg, setMinnAvg] = useState(null);
    const [monthlyPriceByTool, setMonthlyPriceByTool] = useState(null);

    useEffect(() => {
        // Fetch Purchase Volume
        fetch(`${process.env.REACT_APP_API_URL}/api/purchase_volume`)
            .then(response => response.json())
            .then(data => {
                setPurchaseVolume(data.purchase_volume);
                setSma10(data.sma10);
            })
            .catch(error => console.error('Error fetching purchase volume:', error));

        // Fetch Monthly Average Price (Task 2.1)
        fetch(`${process.env.REACT_APP_API_URL}/api/monthly_avg_price`)
            .then(response => response.json())
            .then(data => {
                setDailyPrices(data.daily_prices);
                setMonthlyPrice(data.monthly_price);
            })
            .catch(error => console.error('Error fetching monthly average price:', error));

        // Fetch Monthly Average Price by Tool (Task 2.2)
        fetch(`${process.env.REACT_APP_API_URL}/api/monthly_avg_price_by_tool`)
            .then(response => response.json())
            .then(data => {
                setMinnAvg(data.minn_avg);
                setMonthlyPriceByTool(data.monthly_price);
            })
            .catch(error => console.error('Error fetching monthly average price by tool:', error));
    }, []);

    return (
        <div className="App">
            <h1>SPIMEX Data</h1>
            <div className="data-section">
                <h2>Purchase Volume (Task 3)</h2>
                <p>{purchaseVolume !== null ? `Total Purchase Volume for the month: ${purchaseVolume.toFixed(2)} tons` : 'Loading...'}</p>
                <p>{sma10 !== null ? `SMA10: ${sma10.toFixed(2)}` : 'Loading...'}</p>
            </div>
            <div className="data-section">
                <h2>Monthly Average Price (Task 2.1)</h2>
                <h3>Daily Average Prices:</h3>
                <pre>{dailyPrices ? JSON.stringify(dailyPrices, null, 2) : 'Loading...'}</pre>
                <h3>Monthly Average Price:</h3>
                <pre>{monthlyPrice ? JSON.stringify(monthlyPrice, null, 2) : 'Loading...'}</pre>
            </div>
            <div className="data-section">
                <h2>Monthly Average Price by Tool (Task 2.2)</h2>
                <h3>Min Average Prices:</h3>
                <pre>{minnAvg ? JSON.stringify(minnAvg, null, 2) : 'Loading...'}</pre>
                <h3>Monthly Average Price by Tool:</h3>
                <pre>{monthlyPriceByTool ? JSON.stringify(monthlyPriceByTool, null, 2) : 'Loading...'}</pre>
            </div>
        </div>
    );
}

export default App;
