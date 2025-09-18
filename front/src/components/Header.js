import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css'; // Будет создан позже

function Header() {
    return (
        <header className="App-header">
            <nav>
                <ul>
                    <li><Link to="/">Главная</Link></li>
                    <li><Link to="/quotes">Котировки</Link></li>
                    <li><Link to="/graph">График</Link></li>
                </ul>
            </nav>
        </header>
    );
}

export default Header;
