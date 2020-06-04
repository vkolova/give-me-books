import React from 'react';

const Loading = props =>
    <div className='loading-wrapper' style={{ transform: `scale(${props.scale})` }}>
        <div className={`loader ${props.color}`}>Loading...</div>
    </div>

Loading.defaultProps = {
    color: 'prim',
    scale: 0.65
};

export default Loading;