import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DataTable.css';
import Loader from './Loader';

const DataTable = ({ columns, handleFilterAllData, setFilters, filters }) => {

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [notification, setNotification] = useState('');
  const [allDataLoaded, setAllDataLoaded] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setNotification(`Loading page ${page}...`);
        const response = await axios.get(`http://192.168.10.107:5000/data?page=${page}`);
        // const response = await axios.get(`http://localhost:5000/data?page=${page}`);
        const newData = response.data;

        setTotalRecords(newData.recordsTotal);
        setData(newData.data);
        setLoading(false);
      } catch (err) {
        setError(err);
        setLoading(false);
      }
    };

    fetchData();
  }, [page]);

  const nextPage = () => {
    setPage(prevPage => prevPage + 1);
  };

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(prevPage => prevPage - 1);
    }
  };

  const handleFilterChange = (e, columnName) => {
    const value = e.target.value;
    console.log("handleFilterChange called")
    setFilters(prevFilters => ({
      ...prevFilters,
      [columnName]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const filteredDataLocal = data.filter(item => {
    for (let key in filters) {
      if (filters[key] !== '' && item[key].toLowerCase().indexOf(filters[key].toLowerCase()) === -1) {
        return false;
      }
    }
    return true;
  });

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setNotification('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setLoading(true);
      setButtonsDisabled(true);
      setNotification('Uploading and processing file...');
      const response = await axios.post('http://192.168.10.107:5000/upload_csv', formData, {
      // const response = await axios.post('http://localhost:5000/upload_csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setNotification(response.data.message);
      setLoading(false);
      setButtonsDisabled(false);
      setPage(1);
      window.location.reload();
    } catch (error) {
      setNotification('Error uploading file');
      setLoading(false);
      setButtonsDisabled(false);
    }
  };

  if (loading) {
    return <Loader notification={notification} />;
  }

  if (error) {
    return <p>Error loading data: {error.message}</p>;
  }

  return (
    <div className="table-container">
        <div className="header-container">
            <h2>Total Records : {totalRecords}</h2>
            <h2>Page No. : {page}</h2>
            <div><input type="file" onChange={handleFileChange} />
            <button onClick={handleFileUpload}>Upload CSV</button></div>
        </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            {columns.map((key, idx) => (
              <th key={idx}>{idx + 1}</th>
            ))}
          </tr>
          <tr>
            <th></th>
            {columns.map((key, idx) => (
              <th key={idx}>
                <input
                  type="text"
                  placeholder={`Filter ${idx + 1}`}
                  value={filters[key] || ''}
                  onChange={(e) => handleFilterChange(e, key)}
                />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filteredDataLocal.map((item, index) => (
            <tr key={index}>
              <td>{index + 1 + (page - 1) * 1000}</td>
              {columns.map((key, idx) => (
                <td key={idx}>{item[key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="button-container">
        <button onClick={clearFilters} disabled={loading}>
          Clear Filters
        </button>
        <button onClick={handlePrevPage} disabled={loading || page === 1}>
          Previous Page
        </button>
        <button onClick={nextPage} disabled={loading || allDataLoaded}>
          {loading ? 'Loading...' : 'Next Page'}
        </button>
        <button onClick={() => handleFilterAllData(1, filters)} disabled={loading || allDataLoaded}>
          {loading ? 'Filtering All...' : 'Filter All Data'}
        </button>
      </div>
      {allDataLoaded && <p>All data has been loaded.</p>}
    </div>
  );
};

export default DataTable;
