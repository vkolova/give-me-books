import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { Modal } from 'semantic-ui-react';

class SendToEmail extends React.Component {
    state = {
        email: '',
        open: false
    }

    open = () => {
        this.setState({ open: true })
    }

    handleInputChange = e => {
        this.setState({ [e.target.name]: e.target.value });
    }

    send = () => {
        axios.get('http://localhost:8000/email', {
            params: {
                email: this.state.email,
                search_id: this.props.searchID
            }
        })
            .then(res => this.setState({
                open: false,
                email: ''
            }))
            .catch(err => console.log(err));
    }

    render () {
        return <Modal
            trigger={<a className='a-btn' onClick={this.open}>Прати на мейл</a>}
            size='small'
            open={this.state.open}
        >
            <Modal.Header>Прати на мейл</Modal.Header>
            <Modal.Content>
                <label>
                    <input
                        className='field'
                        name='email'
                        type='email'
                        onChange={this.handleInputChange}
                        style={{
                            marginRight: '5px'
                        }}
                        value={this.state.email}
                    />
                    <div className='btn' onClick={this.send}>Изпрати</div>
                </label>
            </Modal.Content>
        </Modal>;
    }
}

const Footer = ({ canSave, searchID }) =>
    <footer className='footer'>
        {
            canSave &&
            <React.Fragment>
                <a className='a-btn' onClick={window.print}>Изтегли като PDF</a>
                <SendToEmail searchID={searchID}/>
            </React.Fragment>
        }
    </footer>;

Footer.propTypes = {
    canSave: PropTypes.bool,
    searchID: PropTypes.string
};

export default Footer;
