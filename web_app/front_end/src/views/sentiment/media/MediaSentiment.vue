<template>
    <el-row :gutter="20" class="chart-container">
        <el-col :span="24">
            <el-card class="box-card" shadow="never">
                <div slot="header" class="clearfix">
                    <span class="media-header">Media Sentiment Analysis</span>
                </div>
                <el-row :gutter="20">
                    <el-col :span="3">
                        <el-select v-model="selectedTicker" filterable placeholder="Select a ticker">
                            <el-option
                                v-for="ticker in tickers"
                                :key="ticker"
                                :label="ticker"
                                :value="ticker">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="18">
                        <div ref="chart" style="height: 700px;"></div>
                    </el-col>
                    <el-col :span="3">
                        <el-select v-model="selectedRange" @change="applyRangeFilter" placeholder="Select a time range">
                            <el-option label="3 Months" value="3m"></el-option>
                            <el-option label="6 Months" value="6m"></el-option>
                            <el-option label="1 Year" value="1y"></el-option>
                            <el-option label="2 Years" value="2y"></el-option>
                            <el-option label="Full" value="full"></el-option>
                        </el-select>
                    </el-col>
                </el-row>
            </el-card>
        </el-col>
    </el-row>
</template>


<script>
import axios from "axios";
import * as echarts from 'echarts';

export default {
    name: 'MediaSentiment',
    data() {
        return {
            chartInstance: null,
            stockData: [],
            selectedRange: '2y', // Default selection
            allData: [], // This will store all the data
            selectedTicker: '', // Initially empty, will be set after data is fetched
            tickers: [], // To be populated with unique tickers from the data
        };
    },
    mounted() {
        this.drawChart();
    },
    watch: {
        // Watch for changes in selectedTicker to update the chart accordingly
        selectedTicker(newVal, oldVal) {
            if (newVal !== oldVal) {
                // this.applyRangeFilter();
                this.drawChart();
            }
        },
    },
    methods: {
        drawChart() {
            axios.get('../static/media_impact.json').then(response => {
                this.tickers = [...new Set(response.data.map(item => item.ticker))];
                if (this.tickers.length > 0 && !this.selectedTicker) {
                    this.selectedTicker = this.tickers[this.tickers.length - 1]; // Set to first ticker if not already set
                }
                console.log(response.data);
                this.allData = response.data.filter(item => item.ticker === this.selectedTicker);
                this.applyRangeFilter(); // Apply the default range filter
            }).catch(error => {
                console.error("Error:", error);
            });
        },
        applyRangeFilter() {
            // Find the maximum date in the dataset
            const maxDate = new Date(Math.max.apply(null, this.allData.map(e => new Date(e.date))));
            
            // Create new date instance to avoid mutating maxDate
            let startDate = new Date(maxDate.getTime());

            switch(this.selectedRange) {
                case '3m':
                    startDate.setMonth(startDate.getMonth() - 3);
                    break;
                case '6m':
                    startDate.setMonth(startDate.getMonth() - 6);
                    break;
                case '1y':
                    startDate.setFullYear(startDate.getFullYear() - 1);
                    break;
                case '2y':
                    startDate.setFullYear(startDate.getFullYear() - 2);
                    break;
                case 'full':
                    // If 'full' is selected, set startDate to the earliest date in the dataset
                    startDate = new Date(Math.min.apply(null, this.allData.map(e => new Date(e.date))));
                    break;
            }

            // Filter the data based on the startDate
            this.stockData = this.allData.filter(item => {
                const itemDate = new Date(item.date);
                return itemDate >= startDate;
            });

            this.renderChart();
        },
        renderChart() {
            const chartDom = this.$refs.chart;
            const chartInstance = echarts.init(chartDom);
            const dates = this.stockData.map(item => item.date);
            const prices = this.stockData.map(item => item['Adj Close']); // Using 'Adj Close' for price
            const media_impact_indicator = this.stockData.map(item => item.daily_weighted_avg); // Adding daily_weighted_avg
            
            const option = {
                dataZoom: [
                    {
                        type: 'slider', // This is the scrollbar at the bottom
                        start: 0,      // The default zoom – to be updated when the range changes
                        end: 100
                    }
                ],
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                legend: {
                    data: ['Stock Price', 'Media Impact']
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: dates
                },
                yAxis: [
                    {
                        type: 'value',
                        name: 'Media Impact Indicator',
                        min: -0.5,
                        max: 0.5,
                        position: 'left',
                        axisLabel: {
                            formatter: '{value}'
                        }
                    },
                    {
                        type: 'value',
                        name: 'Stock Price',
                        position: 'right',
                        show: true,
                        axisLabel: {
                            formatter: '${value}'
                        }
                    },
                ],
                series: [
                    {
                        name: 'Media Impact',
                        type: 'line',
                        stack: 'Sentiment',
                        areaStyle: {},
                        smooth: true, // Enable smooth lines
                        data: media_impact_indicator,

                    },
                    {
                        name: 'Stock Price',
                        type: 'line',
                        yAxisIndex: 1,
                        smooth: true, // Enable smooth lines
                        data: prices,
                        color: '#ff0000',
                    }
                ]
            };
            chartInstance.setOption(option);
            this.chartInstance = chartInstance;
        },
    },
}
</script>

<style lang="less" scoped>
/* Target the select-ticker class to adjust its width and hide the arrow */
::v-deep .select-ticker .el-select {
    width: 100px; /* Set the width of the left dropdown */
}

/* Hide the arrow icon for the ticker select */
::v-deep .select-ticker .el-input__icon {
    display: none;
}

/* Target the select-range class to adjust its width */
::v-deep .select-range .el-select {
    width: 150px; /* Adjust the width of the right dropdown */
}

/* Optional: Adjust the width of the dropdown menu if needed */
::v-deep .el-select-dropdown {
    width: auto; /* Allow the dropdown menu to adjust its width based on content */
}

// .chart-container .el-col {
//     display: flex;
//     align-items: center; /* This centers the dropdowns vertically */
// }

.media-header {
    font-weight: bold;
    font-size: 20px;
}

.box-card {
    margin-bottom: 20px;
}
</style>
