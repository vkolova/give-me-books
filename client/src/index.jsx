import React from 'react';
import ReactDOM from 'react-dom';

import Header from './Header';
import Search from './Search';
import BookCard from './BookCard';

import './css/index.scss';
import portal from './img/goodreads_portal_matthew_fleming.jpg';


class App extends React.Component {
    render () {
        return <div id='container'>
            {/* <Header /> */}
            {/* <Search/> */}
            <BookCard />
        </div>
    }
}

ReactDOM.render(
    <App/>,
    document.getElementById('root')
);