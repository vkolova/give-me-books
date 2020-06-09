import React from 'react';

const bookdata = {
    url: 'https://www.goodreads.com/book/show/157993.The_Little_Prince',
    title: 'The Little Prince',
    authors: {'Antoine de Saint-Exupéry': 'https://www.goodreads.com/author/show/1020792.Antoine_de_Saint_Exup_ry'},
    cover: 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1367545443l/157993.jpg',
    blurb: 'Moral allegory and spiritual autobiography, The Little Prince is the most translated book in the French language. With a timeless charm it tells the story of a little boy who leaves the safety of his own tiny planet to travel the universe, learning the vagaries of adult behaviour through a series of extraordinary encounters. His personal odyssey culminates in a voyage to Earth and further adventures.'
}

class BookCard extends React.Component {
    render () {
        const { url, title, authors, cover, blurb } = this.props.preview ? bookdata : this.props;

        return <div className='book-card'>        
            <div className='left'>
                <a className='title' href={url} target='_blank'>
                    <img src={cover} />
                </a>
            </div>
            <div className='right'>
                <a className='title' href={url} target='_blank'>{title}</a>
                {
                    Object.keys(authors).map(an =>
                        <a className='author' href={authors[an]} target='_blank'>{an}</a>
                    )
                }
                <p className='blurb'>{`${blurb.substring(0, 350)}...`}</p>
            </div>
        </div>
    }
}

export default BookCard;