import React from 'react';
import axios from 'axios';

import Loading from './Loading';

class Search extends React.Component {
    state = {
        url: '',
        error: false,
        isLoading: false
    }

    updateSearchCriteria = e => {
        this.setState({ url: e.target.value });
    }

    getBookData = () => {
        this.setState({ isLoading: true });
        this.props.app.setState({ isLoadingRecommendations: true });
        axios.get('http://localhost:8000/preview', {
            params: {
                url: this.state.url
            }
        })
        .then(({ data }) => {
            this.props.app.setState({ book: data });
        })
        .catch(err => {
            this.setState({ error: true });
        })
        .then(() => this.setState({ isLoading: false }))

        axios.get('http://localhost:8000/recommendation', {
            params: {
                url: this.state.url
            }
        })
        .then(({ data }) => {
            this.props.app.setState({ recommendations: data.books });
        })
        .catch(err => {
            console.log(err);
        })
        .then(() => this.props.app.setState({ isLoadingRecommendations: false }));
    }

    render () {
        const { isLoading } = this.state;

        return <React.Fragment>
            <div className='search'>
                <input
                    className='field'
                    type='text'
                    onChange={this.updateSearchCriteria}
                    value={this.state.url}
                />
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
        </React.Fragment>
    }
}

export default Search;