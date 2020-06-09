import React from 'react';
import ReactDOM from 'react-dom';

import Header from './Header';
import Search from './Search';
import BookCard from './BookCard';
import BookResults from './BookResults';

import './css/index.scss';

class App extends React.Component {
    state = {
        book: null,
        isLoadingRecommendations: false,
        recommendations: []
    }


    render () {
        const { book, recommendations, isLoadingBookCard, isLoadingRecommendations } = this.state;
    
        return <React.Fragment>
            <div className='main'>
                <Header />
                { !book && <Search app={this} /> }
                { book && <BookCard {...book}/> }
            </div>
            
            { (recommendations.length > 0 || isLoadingRecommendations) && <BookResults books={recommendations} loading={isLoadingRecommendations}/> }
        </React.Fragment>
    }
}

export default App;