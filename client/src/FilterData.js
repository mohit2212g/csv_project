import React, { useState, useEffect } from 'react';
import './DataTable.css';
import axios from 'axios';
import Loader from './Loader';

const FilterData = ({ data, columns, totalRecords, handleFilterChange, filters, handleFilterPrevPage, filterNextPage, filterPage, setFilterPage, allDataLoaded, handleBack, handleFilterAllData }) => {
  const [filterInputs, setFilterInputs] = useState(filters);
  const [filteredDataLocal, setFilteredDataLocal] = useState(data);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState('');

  useEffect(() => {
    setFilteredDataLocal(data);
  }, [data]);

  const handleInputChange = (e, columnName) => {
    const value = e.target.value;
    const updatedFilters = {
      ...filterInputs,
      [columnName]: value,
    };
    setFilterInputs(updatedFilters);

    // Local filtering logic
    const filtered = data.filter(item => {
      for (let key in updatedFilters) {
        if (updatedFilters[key] !== '' && item[key].toLowerCase().indexOf(updatedFilters[key].toLowerCase()) === -1) {
          return false;
        }
      }
      return true;
    });

    setFilteredDataLocal(filtered);
  };

  const applyFilters = () => {
    handleFilterChange(filterInputs);
    handleFilterAllData(1, filterInputs);  // Fetch and render the new filtered data
  };

  const clearFilters = () => {
    const clearedFilters = {};
    setFilterInputs(clearedFilters);
    handleFilterChange(clearedFilters);
    handleFilterAllData(1, clearedFilters);  // Fetch and render the data with cleared filters
  };

  const handleNextPage = () => {
    setFilterPage(filterPage + 1);
    filterNextPage();
  };

  const handlePrevPage = () => {
    setFilterPage(filterPage - 1);
    handleFilterPrevPage();
  };

  const downloadFilteredData = async () => {
    try {
      setLoading(true);
      setNotification(`Downloading Filter Data`);
      setButtonsDisabled(true);

      const response = await axios.get('http://192.168.10.107:5000/download_filtered_data', {
      // const response = await axios.get('http://localhost:5000/download_filtered_data', {
        params: filterInputs,
        responseType: 'blob', 
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'filtered_data.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      setLoading(false);
      setButtonsDisabled(false);
    } catch (error) {
      console.error('Error downloading filtered data:', error);
      setLoading(false); 
      setButtonsDisabled(false);
    }
  };

  if (loading) {
    return <Loader notification={notification} />;
  }

  return (
    <div className="table-container">
      <div className="header-container">
        <button onClick={handleBack}>Back</button>
        <h2>Total Filtered Records: {totalRecords}</h2>
        <h2>Filter Page No. : {filterPage}</h2>
        <button onClick={downloadFilteredData} disabled={loading || buttonsDisabled}>Download Data</button>
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
                  value={filterInputs[key] || ''}
                  onChange={(e) => handleInputChange(e, key)}
                />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filteredDataLocal.map((item, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
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
        <button onClick={handlePrevPage} disabled={loading || filterPage === 1}>
          Previous filterPage
        </button>
        <button onClick={handleNextPage} disabled={loading || allDataLoaded}>
          {loading ? 'Loading...' : 'Next filterPage'}
        </button>
        <button onClick={applyFilters} disabled={loading}>
          Apply Filters
        </button>
      </div>
    </div>
  );
};

export default FilterData;
