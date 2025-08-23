import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
    const [purchaseVolume, setPurchaseVolume] = useState(null);
    const [sma10, setSma10] = useState(null);
    const [dailyPrices, setDailyPrices] = useState(null);
    const [monthlyPrice, setMonthlyPrice] = useState(null);
    const [minnAvg, setMinnAvg] = useState(null);
    const [monthlyPriceByTool, setMonthlyPriceByTool] = useState(null);
    const [tableData, setTableData] = useState(null);
    
    // Используем useRef для хранения предыдущих данных
    const previousTableData = useRef(null);

    const fetchTableData = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/table`);
            const newData = await response.json();
            
            // Сравниваем новые данные с предыдущими
            if (JSON.stringify(newData) !== JSON.stringify(previousTableData.current)) {
                setTableData(newData);
                previousTableData.current = newData;
                console.log('Данные обновлены');
            } else {
                console.log('Данные не изменились');
            }
        } catch (error) {
            console.error('Error fetching table data:', error);
        }
    };

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

        // Первоначальная загрузка данных таблицы
        fetchTableData();

        // Устанавливаем интервал для периодической проверки
        const intervalId = setInterval(fetchTableData, 10000); // 10 секунд

        // Очистка интервала при размонтировании компонента
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="App">
            <h1>SPIMEX Data</h1>
            <div className="data-section">
                <h2>Table Data</h2>
                {tableData ? (
                    <table>
                        <thead>
                            <tr>
                                <th>SID</th>
                                <th>Дата</th>
                                <th>X пред</th>
                                <th>X пред 10</th>
                                <th>X пред 20</th>
                                <th>Текущая</th>
                                <th>Текущая с доставкой</th>
                                <th>Время доставки с отгрузкой</th>
                                <th>Текущая с доставкой P</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.SID}</td>
                                    <td>{row.HIST_CLOSE_DATE}</td>
                                    <td>{row.X_pred_dnya}</td>
                                    <td>{row.X_pred_10_dney}</td>
                                    <td>{row.X_pred_20_dney}</td>
                                    <td>{row.Tekuschaya}</td>
                                    <td>{row.Tekuschaya_s_dostavkoy}</td>
                                    <td>{row.Vremya_dostavki_s_otgruzkoy}</td>
                                    <td>{row.Tekuschaya_s_dostavkoy_P}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    'Loading...'
                )}
            </div>
        </div>
    );
}

export default App;