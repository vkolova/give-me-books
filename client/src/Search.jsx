import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

import Loading from './Loading';

class Shelf extends React.Component {
    handleClick = () => {
        this.props.isSelected
            ? this.props.deselectShelf(this.props.title)
            : this.props.selectShelf(this.props.title);
    }

    render () {
        const { title, isSelected } = this.props;

        return <div
            className={`shelf ${isSelected ? 'selected' : ''}`}
            key={title}
            onClick={this.handleClick}
        >{title}</div>;
    }
}

Shelf.propTypes = {
    title: PropTypes.string,
    isSelected: PropTypes.bool,
    selectShelf: PropTypes.func,
    deselectShelf: PropTypes.func
};

class Search extends React.Component {
    state = {
        url: '',
        error: false,
        sendToEmail: false,
        email: '',
        selectShelves: false,
        allShelves: [],
        selectedShelves: [],
        isLoading: false
    }

    handleInputChange = e => {
        this.setState({ [e.target.name]: e.target.value });
    }

    getBookData = () => {
        this.setState({ isLoading: true });
        this.props.app.setState({ isLoadingRecommendations: true });

        axios.get('http://localhost:8000/preview', {
            params: {
                url: this.state.url
            }
        })
            .then(({ data }) => this.props.app.setState({ book: data }))
            .catch(err => this.setState({ error: true }))
            .then(() => this.setState({ isLoading: false }));

        axios.get('http://localhost:8000/recommendation', {
            params: {
                url: this.state.url,
                ...(
                    this.state.selectShelves &&
                    this.state.selectedShelves.length > 0
                        ? { shelves: this.state.selectedShelves.join(',') }
                        : {}
                )
            }
        })
            .then(({ data }) =>
                this.props.app.setState({
                    recommendations: data.books,
                    searchID: data.search_id
                })
            )
            .catch(err => console.log(err))
            .then(() => this.props.app.setState({ isLoadingRecommendations: false }));
    }

    loadShelves = () => {
        axios.get('http://localhost:8000/shelves', {
            params: {
                url: this.state.url
            }
        })
            .then(({ data }) => this.setState({ allShelves: data.shelves }))
            .catch(err => console.log(err));
    }

    onCheckboxChange = e => {
        this.setState({ [e.target.name]: e.target.checked });
    }

    onSelectShelves = e => {
        this.onCheckboxChange(e);
        e.target.checked && this.state.url && this.loadShelves();
    }

    selectShelf = shelf => {
        this.setState({ selectedShelves: [shelf, ...this.state.selectedShelves] });
    }

    deselectShelf = shelf => {
        this.setState({ selectedShelves: this.state.selectedShelves.filter(s => s !== shelf) });
    }

    render () {
        const { isLoading, selectShelves } = this.state;

        return <React.Fragment>
            <div className='search'>
                <input
                    className='field'
                    name='url'
                    type='text'
                    onChange={this.handleInputChange}
                    value={this.state.url}
                />
                <div className='search-options'>
                    <label>
                        <input type='checkbox' name='selectShelves' value={selectShelves} onChange={this.onSelectShelves} />
                        Искам да избера ключовите категории
                    </label>
                </div>
                {
                    this.state.sendToEmail &&
                        <input
                            className='field'
                            name='email'
                            type='email'
                            onChange={this.handleInputChange}
                            value={this.state.email}
                        />
                }
                <div className='shelves'>
                    {
                        this.state.allShelves.map(s =>
                            <Shelf
                                key={s}
                                title={s}
                                isSelected={this.state.selectedShelves.includes(s)}
                                selectShelf={this.selectShelf}
                                deselectShelf={this.deselectShelf}
                            />
                        )
                    }
                </div>
                {
                    isLoading
                        ? <div className='btn'><Loading color='white' scale={0.2} /></div>
                        : <div className='btn' onClick={this.getBookData}>Търси</div>
                }
            </div>
            {
                this.state.error
                    ? <div className='error-message'>
                        О, не! Възникна грешка. Въвел ли си валиден линк?
                    </div>
                    : <div style={{ height: '25px' }}/>
            }
        </React.Fragment>;
    }
}

Search.propTypes = {
    app: PropTypes.element
};

export default Search;
