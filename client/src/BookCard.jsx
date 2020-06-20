import React from 'react';
import PropTypes from 'prop-types';

const BookCard = ({ url, title, series, authors, cover, blurb }) =>
    <div className='book-card' key={url}>
        <div className='left'>
            <a className='title' href={url} target='_blank' rel='noreferrer'>
                <img src={cover} />
            </a>
        </div>
        <div className='right'>
            <a className='title' href={url} target='_blank' rel='noreferrer'>{title}</a>
            <br />
            {
                series &&
                <React.Fragment>
                    <a className='series' href={series.url} target='_blank' rel='noreferrer'>{series.title}</a>
                    <br />
                </React.Fragment>
            }
            {
                Object.keys(authors).map(an =>
                    <a
                        className='author'
                        key={an.replace(' ', '-')}
                        href={authors[an]}
                        target='_blank'
                        rel='noreferrer'
                    >{an}</a>
                )
            }
            <p className='blurb'>
                {`${blurb.substring(0, 500)}...`}
            </p>
        </div>
    </div>;

BookCard.propTypes = {
    url: PropTypes.string,
    title: PropTypes.string,
    authors: PropTypes.object,
    cover: PropTypes.string,
    series: PropTypes.any,
    blurb: PropTypes.string
};

export default BookCard;
