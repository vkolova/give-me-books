import React from 'react';

class BookCard extends React.Component {
    render () {
        const props = {
            title: 'The Little Prince',
            author: 'Antoine de Saint-Exupéry',
            cover: 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367545443l/157993.jpg',
            blurb: 'Moral allegory and spiritual autobiography, The Little Prince is the most translated book in the French language. With a timeless charm it tells the story of a little boy who leaves the safety of his own tiny planet to travel the universe, learning the vagaries of adult behaviour through a series of extraordinary encounters. His personal odyssey culminates in a voyage to Earth and further adventures.'
        }

        const { title, author, cover, blurb } = props;

        return <div className='book-card'>        
            <div className='left'>
                <img src={cover} />
            </div>
            <div className='right'>
                <div className='title'>{title}</div>
                <div className='author'>{author}</div>
                <p className='blurb'>{blurb}</p>
            </div>
        </div>
    }
}

export default BookCard;