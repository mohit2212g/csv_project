#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
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

int main() {
    std::ifstream file("123_Output.csv");
    if (!file.is_open()) {
        std::cerr << "Unable to open file\n";
        return 1;
    }

    sqlite3* db;
    if (sqlite3_open("data.db", &db)) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << "\n";
        return 1;
    }

    // Read the first row to determine the number of columns
    std::string first_line;
    std::getline(file, first_line);
    std::stringstream ss(first_line);
    std::vector<std::string> columns;
    std::string token;
    while (std::getline(ss, token, ',')) {
        columns.push_back(token);
    }

    // Create table dynamically
    std::string create_table_sql = "BEGIN TRANSACTION; CREATE TABLE IF NOT EXISTS data (";
    for (size_t i = 0; i < columns.size(); ++i) {
        create_table_sql += "col" + std::to_string(i + 1) + " TEXT";
        if (i < columns.size() - 1) {
            create_table_sql += ", ";
        }
    }
    create_table_sql += ");";
    
    char* errMsg = nullptr;
    if (sqlite3_exec(db, create_table_sql.c_str(), nullptr, nullptr, &errMsg) != SQLITE_OK) {
        std::cerr << "SQL error: " << errMsg << "\n";
        sqlite3_free(errMsg);
    }

    // Prepare insert statement dynamically
    std::string insert_sql = "INSERT INTO data (";
    for (size_t i = 0; i < columns.size(); ++i) {
        insert_sql += "col" + std::to_string(i + 1);
        if (i < columns.size() - 1) {
            insert_sql += ", ";
        }
    }
    insert_sql += ") VALUES (";
    for (size_t i = 0; i < columns.size(); ++i) {
        insert_sql += "?";
        if (i < columns.size() - 1) {
            insert_sql += ", ";
        }
    }
    insert_sql += ");";
    
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, insert_sql.c_str(), -1, &stmt, NULL);

    // Rewind the file to the beginning
    file.clear();
    file.seekg(0, std::ios::beg);

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
