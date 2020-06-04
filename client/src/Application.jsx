import React from 'react';
import ReactDOM from 'react-dom';

import Header from './Header';
import Search from './Search';
import BookCard from './BookCard';
import BookResults from './BookResults';
import Loading from './Loading';

import './css/index.scss';

class App extends React.Component {
    state = {
        book: null,
        recommendations: []
    }


    render () {
        const { book, recommendations, isLoadingBookCard } = this.state;
    
        return <React.Fragment>
            <div className='main'>
                <Header />
                { !book && <Search app={this} /> }
                { book && <BookCard {...book}/> }
            </div>
            
            { recommendations.length > 0 && <BookResults books={Array(10).fill().map((_, i) => i + 1)} /> }
        </React.Fragment>
    }
}

export default App;