import React from 'react';

import Main from './Main';
import Search from './Search';
import BookCard from './BookCard';
import BookResults from './BookResults';
import Header from './Header';
import Footer from './Footer';

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
            <Header />
            <div className='content-wrapper'>
                <div className='half main'>
                    <Main loaded={recommendations.length > 0 || isLoadingBookCard || isLoadingRecommendations} />
                    { !book && <Search app={this} /> }
                    { book && <BookCard {...book}/> }
                </div>
                {
                    (recommendations.length > 0 || isLoadingRecommendations) &&
                    <BookResults books={recommendations} loading={isLoadingRecommendations}/>
                }
            </div>
            <Footer />
        </React.Fragment>;
    }
}

export default App;
