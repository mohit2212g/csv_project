import React, { useState, useEffect } from 'react';
import DataTable from './DataTable';
import Loader from './Loader';
import FilterData from './FilterData';
import axios from 'axios';

function App() {
  const [showFilteredData, setShowFilteredData] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState('');
  const [filters, setFilters] = useState({});
  const [filteredData, setFilteredData] = useState([]);
  const [filterPage, setFilterPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    const fetchColumns = async () => {
      try {
        const response = await axios.get('http://192.168.10.107:5000/get_columns');
        // const response = await axios.get('http://localhost:5000/get_columns');
        setColumns(response.data);
        setLoading(false); 
      } catch (err) {
        setNotification('Error fetching columns');
        setLoading(false);
      }
    };

    fetchColumns();
  }, []);

  // const columns = [
  //   'col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10',
  //   'col11', 'col12', 'col13', 'col14', 'col15', 'col16', 'col17', 'col18', 'col19', 'col20',
  //   'col21', 'col22', 'col23', 'col24', 'col25', 'col26', 'col27', 'col28', 'col29', 'col30', 'col31','col32',
  //   'col33', 'col34', 'col35', 'col36', 'col37', 'col38', 'col39', 'col40'
  // ];

  useEffect(() => {
    setLoading(false); 
  }, []);

  const handleFilterAllData = async (filterPage, filters) => {
    try {
      setFilterPage(filterPage)
      setLoading(true);
      setNotification(`Loading Filter Page ${filterPage}...`);
      
      const filterParams = { ...filters, filterPage };
      const response = await axios.get('http://192.168.10.107:5000/filter_data', {
      // const response = await axios.get('http://localhost:5000/filter_data', {
        params: filterParams
      });
      const newData = response.data;

      console.log("data : ", newData)

      setTotalRecords(newData.recordsTotal);
      setFilteredData(newData.data);
      setLoading(false);
      setShowFilteredData(true);
    } catch (err) {
      setNotification('Error applying filters');
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleGoBack = () => {
    setShowFilteredData(false);
  };

  if (loading) {
    return <Loader notification={notification} />;
  }

  return (
    <div className="App">
      <header className="App-header">
        {showFilteredData ? (
          <FilterData
            data={filteredData}
            columns={columns}
            totalRecords={totalRecords}
            handleFilterChange={handleFilterChange}
            filters={filters}
            handleFilterPrevPage={() => handleFilterAllData(filterPage - 1, filters)}
            filterNextPage={() => handleFilterAllData(filterPage + 1, filters)}
            loading={loading}
            filterPage={filterPage}
            setFilterPage={setFilterPage}
            allDataLoaded={filteredData.length === 0}
            handleBack={handleGoBack}
            handleFilterAllData={handleFilterAllData} // Pass the function here
          />
        ) : (
          <DataTable columns={columns} handleFilterAllData={handleFilterAllData} setFilters={setFilters} filters={filters} />
        )}
      </header>
    </div>
  );
}

export default App;
