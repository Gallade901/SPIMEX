import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Header from './components/Header';
import Quotes from './pages/Quotes';
import Graph from './pages/Graph'; // Будет создан позже
import { Route, Routes } from 'react-router-dom';

function App() {
    const [tableData, setTableData] = useState(null);
    
    const previousTableData = useRef(null);

    const fetchTableData = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/table`);
            const newData = await response.json();
            
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

    // Функция для форматирования чисел с двумя знаками после запятой
    const formatNumber = (value) => {
        if (value === null || value === undefined) return '';
        const num = parseFloat(value);
        return isNaN(num) ? value : num.toFixed(2);
    };

    useEffect(() => {
    
        fetchTableData();

        const intervalId = setInterval(fetchTableData, 10000);
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="App">
            <Header />
            <Routes>
                <Route path="/" element={ 
                    <>
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
                                            <th>X текущая</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {tableData.map((row, index) => (
                                            <tr key={index}>
                                                <td>{row.SID}</td>
                                                <td>{row.HIST_CLOSE_DATE}</td>
                                                <td>{formatNumber(row.X_pred_dnya)}</td>
                                                <td>{formatNumber(row.X_pred_10_dney)}</td>
                                                <td>{formatNumber(row.X_pred_20_dney)}</td>
                                                <td>{formatNumber(row.Tekuschaya)}</td>
                                                <td>{formatNumber(row.Tekuschaya_s_dostavkoy)}</td>
                                                <td>{row.Vremya_dostavki_s_otgruzkoy}</td>
                                                <td>{formatNumber(row.Tekuschaya_s_dostavkoy_P)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                'Loading...'
                            )}
                        </div>
                    </>
                } />
                <Route path="/quotes" element={<Quotes />} />
                <Route path="/graph" element={<Graph />} />
            </Routes>
        </div>
    );
}

export default App;