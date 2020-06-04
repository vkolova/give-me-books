import React from 'react';

import portal from './img/goodreads_portal_matthew_fleming.jpg';

const Header = () =>
    <div className='header'>
        <img className='portal' src={portal} alt='Goodreads Portal by Matthew Fleming'/>
        <h1>Препоръчай ми книги, като...</h1>
        <p>Защото няма такова нещо като „твърде много книги“.</p>
    </div>


export default Header;