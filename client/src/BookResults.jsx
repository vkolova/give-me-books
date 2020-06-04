import React from 'react';
import BookCard from './BookCard';

const BookResults = props => {
    return <div className='books-list'>
        <h1>Опитай...</h1>
        {
            props.books.map((b, i) => <BookCard preview={true} />)
        }
        <div className='fade-bottom'/>
    </div>
}

export default BookResults;