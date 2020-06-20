import React from 'react';


const Main = props =>
    <div className='site-title'>
        {
            props.loaded
                ? <h1>Kниги, като...</h1>
                : <React.Fragment>
                    <h1>Препоръчай ми книги, като...</h1>
                    <p>Защото няма такова нещо като „твърде много книги“.</p>
                </React.Fragment>
        }
    </div>

export default Main;