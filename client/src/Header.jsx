import React from 'react';

import logo from './img/reading.png';

const Header = () =>
    <header className='header'>
        <a href='/'><img className='logo' src={logo} alt='Opened book with bookmark'/></a>
    </header>;

export default Header;