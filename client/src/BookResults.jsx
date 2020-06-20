import React from 'react';
import PropTypes from 'prop-types';

import BookCard from './BookCard';
import Loading from './Loading';

const BookResults = props =>
    <div className='half books-list'>
        {
            props.loading
                ? <div className='center'><Loading/></div>
                : <React.Fragment>
                    <h1>Опитай...</h1>
                    {
                        props.books.map((b, i) => <BookCard key={b.title.replace(' ', '-')} {...b} />)
                    }
                    <div className='fade-bottom'/>
                </React.Fragment>
        }
    </div>;

BookResults.propTypes = {
    loading: PropTypes.bool,
    books: PropTypes.arrayOf(PropTypes.object)
};

export default BookResults;
