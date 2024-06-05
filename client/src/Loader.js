import React from 'react';
import './Loader.css';

const Loader = ({ notification }) => {
    return (
        <div className="loader-container">
            <div className="loader"></div>
            <p>{ notification } </p>
        </div>
    );
};

export default Loader;
