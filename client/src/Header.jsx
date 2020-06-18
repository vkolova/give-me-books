import React from 'react';

import portal from './img/goodreads_portal_matthew_fleming.jpg';

const Header = () =>
    <div className='header'>
        <a href='/'><img className='portal' src={portal} alt='Goodreads Portal by Matthew Fleming'/></a>
    </div>;

export default Header;