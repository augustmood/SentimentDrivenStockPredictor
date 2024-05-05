<template>
    <div>
        <el-row :gutter="20" class="chart-container">
            <el-col :span="24">
                <el-card class="box-card" shadow="never">
                    <div slot="header" class="clearfix">
                        <span class="stock-price-header">Stock Price</span>
                    </div>
                    <el-row :gutter="20">
                        <el-col :span="3">
                            <el-select v-model="selectedTickers" multiple placeholder="Select tickers">
                                <el-option v-for="item in tickers" :key="item" :label="item" :value="item"></el-option>
                            </el-select>
                        </el-col>
                        <el-col :span="18">
                            <div ref="chart" style="width: 100%; height: 600px;"></div>
                        </el-col>
                        <el-col :span="3">
                            <el-select v-model="selectedTimeRange" placeholder="Select time range">
                                <el-option v-for="range in timeRanges" :key="range.value" :label="range.label" :value="range.value"></el-option>
                            </el-select>
                        </el-col>
                    </el-row>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20" class="chart-container">
            <el-col :span="24">
                <el-card class="box-card" shadow="never">
                    <div slot="header" class="clearfix">
                        <span class="stock-price-header">Last 5 Days Stock Price</span>
                    </div>
                    <el-row :gutter="20">
                        <el-col :span="24">
                            <el-table :data="tableData" style="width: 100%" stripe>
                                <el-table-column prop="date" label="Date" sortable></el-table-column>
                                <el-table-column prop="Open" label="Open" sortable></el-table-column>
                                <el-table-column prop="High" label="High" sortable></el-table-column>
                                <el-table-column prop="Low" label="Low" sortable></el-table-column>
                                <el-table-column prop="Close" label="Close" sortable></el-table-column>
                                <el-table-column prop="Adj Close" label="Adj Close" sortable></el-table-column>
                                <el-table-column prop="Volume" label="Volume" sortable></el-table-column>
                                <el-table-column prop="ticker" label="Ticker" sortable></el-table-column>
                            </el-table>
                        </el-col>
                    </el-row>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>
  
  <script>
  import * as echarts from 'echarts';
  import axios from 'axios';
  
  export default {
    name: 'StockChart',
    data() {
      return {
        chartInstance: null,
        allStockData: [], // To store all fetched stock data
        selectedTickers: ['AAPL', 'NVDA', 'TSLA'], // Default selected tickers
        selectedTimeRange: '1Y', // Selected time range
        tickers: [], // Available tickers for selection
        timeRanges: [ // Define your time ranges here
          { label: 'Last Month', value: '1M' },
          { label: 'Last 3 Months', value: '3M' },
          { label: 'Last 6 Months', value: '6M' },
          { label: 'Last Year', value: '1Y' },
          { label: 'Last 5 Years', value: '5Y' },
        ],
        tableData: [], // Full dataset
        currentPageData: [], // Data for the current page
        currentPage: 1,
        pageSize: 20, // Number of items per page
        totalItems: 0, // Total number of items in the dataset
      };
    },
    watch: {
        selectedTickers: {
            handler(newVal, oldVal) {
            if (newVal !== oldVal) {
                this.filterAndInitChart();
            }
            },
            immediate: true // This ensures the watcher is triggered upon component initialization
        },
        selectedTimeRange: {
            handler(newVal, oldVal) {
            if (newVal !== oldVal) {
                this.filterAndInitChart();
            }
            },
            immediate: true // This ensures the watcher is triggered upon component initialization
        },
    },
    methods: {
        async fetchStockData() {
        try {
            const response = await axios.get('static/stock_full_data.json');
            this.allStockData = response.data;
            const sortedData = response.data.sort((a, b) => new Date(b.date) - new Date(a.date));
            this.tableData = sortedData.slice(0, 10);
            this.totalItems = this.tableData.length;
            console.log(this.tableData)
            this.setCurrentPageData();
            // Dynamically populate tickers based on fetched data
            this.tickers = [...new Set(response.data.map(item => item.ticker))];

            // Automatically select a few tickers as initially selected, if needed
            // This line selects the first three tickers; adjust as necessary
            this.selectedTickers = this.tickers.slice(0, 3);

            this.filterAndInitChart();
            } catch (error) {
                console.error('Error fetching stock data:', error);
            }
        },
      filterAndInitChart() {
        // First, filter based on selectedTickers
        let filteredData = this.allStockData.filter(item => this.selectedTickers.includes(item.ticker));

        // Implement time range filtering based on selectedTimeRange
        if (this.selectedTimeRange) {
            const endDate = new Date();
            let startDate = new Date();

            switch (this.selectedTimeRange) {
            case '1M':
                startDate.setMonth(endDate.getMonth() - 1);
                break;
            case '3M':
                startDate.setMonth(endDate.getMonth() - 3);
                break;
            case '6M':
                startDate.setMonth(endDate.getMonth() - 6);
                break;
            case '1Y':
                startDate.setFullYear(endDate.getFullYear() - 1);
                break;
            case '5Y':
                startDate.setFullYear(endDate.getFullYear() - 5);
                break;
            default:
                break;
            }

            filteredData = filteredData.filter(item => {
            const itemDate = new Date(item.date);
            return itemDate >= startDate && itemDate <= endDate;
            });
        }

        // Proceed to initialize chart with filtered data
        this.initChart(filteredData);
        },
        initChart(stockData) {
            const series = this.selectedTickers.map(ticker => ({
                name: ticker,
                type: 'line',
                data: stockData
                    .filter(item => item.ticker === ticker)
                    .map(item => [item.date, item['Adj Close']])
            }));

            const option = {
                dataZoom: [
                    {
                        type: 'slider', // This is the scrollbar at the bottom
                        start: 0,      // The default zoom – to be updated when the range changes
                        end: 100
                    }
                ],
                backgroundColor: '#f5f5f5',
                tooltip: {
                    trigger: 'axis',
                },
                legend: {
                    data: this.selectedTickers
                },
                xAxis: {
                    type: 'category',
                    data: this.getXAxisData(stockData),
                },
                yAxis: {
                    type: 'value',
                },
                series: series,
            };

            // Use setOption with notMerge set to true to clear previous data
            this.chartInstance.clear(); // Clear the chart before setting new options
            this.chartInstance.setOption(option, true);
        },

        // Added method to generalize X-axis data calculation
        getXAxisData(stockData) {
            // Create a set to store unique dates
            const dateSet = new Set();

            // Aggregate dates from all selected tickers
            this.selectedTickers.forEach(ticker => {
                stockData
                .filter(item => item.ticker === ticker)
                .forEach(item => dateSet.add(item.date));
            });

            // Convert the set of dates into an array and sort it
            let dates = Array.from(dateSet);
            dates.sort((a, b) => {
                const dateA = new Date(a), dateB = new Date(b);
                return dateA - dateB;
            });

            return dates;
        },

        handlePageChange(page) {
            this.currentPage = page;
            this.setCurrentPageData();
        },

        setCurrentPageData() {
            const startIndex = (this.currentPage - 1) * this.pageSize;
            const endIndex = startIndex + this.pageSize;
            this.currentPageData = this.tableData.slice(startIndex, endIndex);
        },
    },
    mounted() {
      this.chartInstance = echarts.init(this.$refs.chart);
      this.fetchStockData();
    },
  }
  </script>
  
  <style scoped>
  .el-row {
    margin-bottom: 20px;
    &:last-child {
      margin-bottom: 0;
    }
  }
  .el-col {
    border-radius: 4px;
  }
  .bg-purple-dark {
    background: #99a9bf;
  }
  .grid-content {
    border-radius: 4px;
    min-height: 36px;
  }

  .charts-content {
    border-radius: 4px;
  }

  .chart-container {
    margin: 20px auto;
    /* max-width: 1200px; Adjust based on your layout */
}

.box-card {
    padding: 0px 20px 20px 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.clearfix:before,
.clearfix:after {
    display: table;
    content: " ";
    clear: both;
}

.mb {
    margin-bottom: 20px;
}

.stock-price-header {
    font-weight: 600; /* Makes the font bolder */
    font-size: 24px; /* Increases the font size */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Example font family */
}

  </style>