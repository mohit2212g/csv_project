#include <iterator>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <string_view>
#include <sqlite3.h>

std::vector<std::string> getNextLineAndSplitIntoTokens(std::istream& str) {
    std::vector<std::string> result;
    std::string line;
    std::getline(str, line);

    std::stringstream lineStream(line);
    std::string cell;

    while (std::getline(lineStream, cell, ',')) {
        result.push_back(cell);
    }
    if (!lineStream && cell.empty()) {
        result.push_back("");
    }
    return result;
}

class CSVRow {
public:
    std::string_view operator[](std::size_t index) const {
        return std::string_view(&m_line[m_data[index] + 1], m_data[index + 1] - (m_data[index] + 1));
    }
    std::size_t size() const {
        return m_data.size() - 1;
    }
    void readNextRow(std::istream& str) {
        std::getline(str, m_line);
        m_data.clear();
        m_data.emplace_back(-1);
        std::string::size_type pos = 0;
        while ((pos = m_line.find(',', pos)) != std::string::npos) {
            m_data.emplace_back(pos);
            ++pos;
        }
        pos = m_line.size();
        m_data.emplace_back(pos);
    }
private:
    std::string m_line;
    std::vector<int> m_data;
};

std::istream& operator>>(std::istream& str, CSVRow& data) {
    data.readNextRow(str);
    return str;
}

class CSVIterator {
public:
    typedef std::input_iterator_tag iterator_category;
    typedef CSVRow value_type;
    typedef std::size_t difference_type;
    typedef CSVRow* pointer;
    typedef CSVRow& reference;

    CSVIterator(std::istream& str) : m_str(str.good() ? &str : nullptr) { ++(*this); }
    CSVIterator() : m_str(nullptr) {}

    CSVIterator& operator++() { if (m_str) { if (!((*m_str) >> m_row)) { m_str = nullptr; } } return *this; }
    CSVIterator operator++(int) { CSVIterator tmp(*this); ++(*this); return tmp; }
    CSVRow const& operator*() const { return m_row; }
    CSVRow const* operator->() const { return &m_row; }

    bool operator==(CSVIterator const& rhs) { return ((this == &rhs) || ((this->m_str == nullptr) && (rhs.m_str == nullptr))); }
    bool operator!=(CSVIterator const& rhs) { return !((*this) == rhs); }
private:
    std::istream* m_str;
    CSVRow m_row;
};

class CSVRange {
std::istream& stream;
public:
    CSVRange(std::istream& str) : stream(str) {}
    CSVIterator begin() const { return CSVIterator{stream}; }
    CSVIterator end() const { return CSVIterator{}; }
};

void clearDatabase(sqlite3* db) {
    char* errMsg = nullptr;
    const char* sql = "DELETE FROM data;";
    if (sqlite3_exec(db, sql, nullptr, nullptr, &errMsg) != SQLITE_OK) {
        std::cerr << "SQL error: " << errMsg << "\n";
        sqlite3_free(errMsg);
        sqlite3_close(db);
        exit(1); // Exit the program if clearing fails
    }
    std::cout << "Database cleared successfully.\n";
}

int main() {
    std::ifstream file("123_Output.CSV");
    if (!file.is_open()) {
        std::cerr << "Unable to open file\n";
        return 1;
    }

    sqlite3* db;
    if (sqlite3_open("data.db", &db)) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << "\n";
        return 1;
    }

    // Clear the database
    //clearDatabase(db);

    const char* sql = "BEGIN TRANSACTION;"
                      "CREATE TABLE IF NOT EXISTS data ("
                      "col1 TEXT, col2 TEXT, col3 TEXT, col4 TEXT, col5 TEXT, "
                      "col6 TEXT, col7 TEXT, col8 TEXT, col9 TEXT, col10 TEXT, "
                      "col11 TEXT, col12 TEXT, col13 TEXT, col14 TEXT, col15 TEXT, "
                      "col16 TEXT, col17 TEXT, col18 TEXT, col19 TEXT, col20 TEXT, "
                      "col21 TEXT, col22 TEXT, col23 TEXT, col24 TEXT, col25 TEXT, "
                      "col26 TEXT, col27 TEXT, col28 TEXT, col29 TEXT, col30 TEXT, "
                      "col31 TEXT);";
    char* errMsg = nullptr;
    if (sqlite3_exec(db, sql, nullptr, nullptr, &errMsg) != SQLITE_OK) {
        std::cerr << "SQL error: " << errMsg << "\n";
        sqlite3_free(errMsg);
    }

    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "INSERT INTO data (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17, col18, col19, col20, col21, col22, col23, col24, col25, col26, col27, col28, col29, col30, col31) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", -1, &stmt, NULL);

    for (auto& row : CSVRange(file)) {
        for (int i = 0; i < row.size(); ++i) {
            sqlite3_bind_text(stmt, i + 1, row[i].data(), row[i].size(), SQLITE_STATIC);
        }
        sqlite3_step(stmt);
        sqlite3_reset(stmt);
    }

    sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    sqlite3_finalize(stmt);
    sqlite3_close(db);

    return 0;
}
