import React from 'react';
import PropTypes from 'prop-types';

const Link = ({ cn, href, children }) =>
    <a className={cn} href={href} target='_blank' rel='noreferrer'>
        {children}
    </a>;

Link.propTypes = {
    cn: PropTypes.string,
    href: PropTypes.string
};

const BookCard = ({ url, title, series, authors, cover, blurb }) =>
    <div className='book-card' key={url}>
        <div className='left'>
            <Link cn='title' href={url}><img src={cover} /></Link>
        </div>
        <div className='right'>
            <Link cn='title' href={url}>{title}</Link>
            <br />
            {
                series &&
                <React.Fragment>
                    <Link cn='series' href={series.url}>
                        {series.title}
                    </Link>
                    <br />
                </React.Fragment>
            }
            {
                Object.keys(authors).map(an =>
                    <Link cn='author' href={authors[an]} key={authors[an]}>{an}</Link>
                )
            }
            <p className='blurb'>{`${blurb.substring(0, 500)}...`}</p>
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
