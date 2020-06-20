import React from 'react';
import BookCard from './BookCard';
import Loading from './Loading';

const BookResults = props => {
    return <div className='half books-list'>
        {
            props.loading
            ? <div className='center'><Loading/></div>
            : <React.Fragment>
                <h1>Опитай...</h1>
                {
                    props.books.map((b, i) => <BookCard {...b} />)
                }
                <div className='fade-bottom'/>
            </React.Fragment>
        }
    </div>
}

export default BookResults;