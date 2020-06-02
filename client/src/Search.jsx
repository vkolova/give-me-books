import React from 'react';

class Search extends React.Component {
    state = {
        url: ''
    }

    render () {
        return <div className='search'>
            <div className='field-wrapper'>
                <input className='field' type='text'/>
            </div>
            <div className='btn'>Търси</div>
        </div>
    }
}

export default Search;